from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from apps.historical.models import WaitlistObservation
from .models import ModelVersion

TARGETS = ("CNF", "RAC", "WL")
CATEGORICAL = ("train_number", "source_code", "destination_code", "travel_class", "quota")
NUMERIC = ("initial_waitlist", "current_waitlist", "days_remaining", "wl_movement")
FEATURE_VERSION = "wl-v1"


def _feature_frame(records):
    rows = []
    for row in records:
        rows.append({
            "journey_key": str(row["journey_key"]),
            "journey_date": row["journey_date"],
            "train_number": row["train__number"],
            "source_code": row["source_station__code"],
            "destination_code": row["destination_station__code"],
            "travel_class": row["travel_class"],
            "quota": row["quota"],
            "initial_waitlist": row["initial_waitlist"],
            "current_waitlist": row["current_waitlist"],
            "days_remaining": row["days_remaining"],
            "wl_movement": row["initial_waitlist"] - row["current_waitlist"],
            "final_outcome": row["final_outcome"],
        })
    return pd.DataFrame(rows)


def _pipeline(estimator, scale_numeric=False):
    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))
    preprocess = ColumnTransformer([
        ("categorical", OneHotEncoder(handle_unknown="ignore"), list(CATEGORICAL)),
        ("numeric", Pipeline(numeric_steps), list(NUMERIC)),
    ])
    return Pipeline([("features", preprocess), ("classifier", estimator)])


def _scores(model, x, y):
    probabilities = model.predict_proba(x)
    classes = list(model.classes_)
    labels = list(y)
    loss = log_loss(labels, probabilities, labels=classes)
    one_hot = np.zeros((len(labels), len(classes)))
    positions = {label: index for index, label in enumerate(classes)}
    for row_index, label in enumerate(labels):
        one_hot[row_index, positions[label]] = 1
    brier = float(np.mean(np.sum((one_hot - probabilities) ** 2, axis=1)))
    accuracy = float(accuracy_score(labels, model.predict(x)))
    return {"log_loss": float(loss), "brier_score": brier, "accuracy": accuracy}


def train_confirmation_model():
    values = WaitlistObservation.objects.select_related("train", "source_station", "destination_station").values(
        "journey_key", "journey_date", "train__number", "source_station__code", "destination_station__code",
        "travel_class", "quota", "initial_waitlist", "current_waitlist", "days_remaining", "final_outcome",
    )
    frame = _feature_frame(values)
    if frame.empty:
        raise ValueError("No historical observations exist yet; import de-identified CSV data first.")
    groups = frame["journey_key"].drop_duplicates().tolist()
    if len(groups) < 40:
        raise ValueError(f"At least 40 distinct journey groups are required; found {len(groups)}.")
    if set(frame["final_outcome"].unique()) != set(TARGETS):
        raise ValueError("Training data must contain CNF, RAC, and WL outcomes.")

    group_dates = frame.groupby("journey_key")["journey_date"].max().sort_values()
    first_cut = max(1, min(len(group_dates) - 2, int(len(group_dates) * 0.70)))
    second_cut = max(first_cut + 1, min(len(group_dates) - 1, int(len(group_dates) * 0.85)))
    train_groups = set(group_dates.index[:first_cut])
    validation_groups = set(group_dates.index[first_cut:second_cut])
    test_groups = set(group_dates.index[second_cut:])
    train_rows = frame[frame["journey_key"].isin(train_groups)]
    validation_rows = frame[frame["journey_key"].isin(validation_groups)]
    test_rows = frame[frame["journey_key"].isin(test_groups)]
    if set(train_rows["final_outcome"].unique()) != set(TARGETS) or validation_rows.empty or test_rows.empty:
        raise ValueError("Chronological train/validation/test split needs all outcomes in training and later journeys in validation and test.")

    x_train = train_rows[list(CATEGORICAL + NUMERIC)]
    y_train = train_rows["final_outcome"]
    groups_train = train_rows["journey_key"]
    x_validation = validation_rows[list(CATEGORICAL + NUMERIC)]
    y_validation = validation_rows["final_outcome"]
    x_test = test_rows[list(CATEGORICAL + NUMERIC)]
    y_test = test_rows["final_outcome"]
    fold_count = min(5, train_rows["journey_key"].nunique())
    if fold_count < 2:
        raise ValueError("Not enough separate journeys for group-aware model calibration.")
    cv = GroupKFold(n_splits=fold_count)

    candidates = [
        ("logistic_regression", _pipeline(LogisticRegression(max_iter=1000, class_weight="balanced"), scale_numeric=True)),
        ("calibrated_random_forest", CalibratedClassifierCV(
            estimator=_pipeline(RandomForestClassifier(n_estimators=250, min_samples_leaf=2, class_weight="balanced_subsample", random_state=42)),
            method="sigmoid",
            cv=cv,
        )),
    ]
    evaluated = []
    for name, model in candidates:
        if name == "calibrated_random_forest":
            model.fit(x_train, y_train, groups=groups_train)
        else:
            model.fit(x_train, y_train)
        validation_metrics = _scores(model, x_validation, y_validation)
        evaluated.append((validation_metrics["log_loss"], name, model))
    _, algorithm, selected = min(evaluated, key=lambda item: item[0])

    # Refit the chosen approach on train + validation; the final test period stays untouched.
    fit_rows = frame[frame["journey_key"].isin(train_groups | validation_groups)]
    fit_x = fit_rows[list(CATEGORICAL + NUMERIC)]
    fit_y = fit_rows["final_outcome"]
    fit_groups = fit_rows["journey_key"]
    if algorithm == "calibrated_random_forest":
        refit = CalibratedClassifierCV(
            estimator=_pipeline(RandomForestClassifier(n_estimators=250, min_samples_leaf=2, class_weight="balanced_subsample", random_state=42)),
            method="sigmoid",
            cv=GroupKFold(n_splits=min(5, fit_rows["journey_key"].nunique())),
        )
        refit.fit(fit_x, fit_y, groups=fit_groups)
    else:
        refit = _pipeline(LogisticRegression(max_iter=1000, class_weight="balanced"), scale_numeric=True)
        refit.fit(fit_x, fit_y)
    selected = refit
    metrics = _scores(selected, x_test, y_test)

    configured_path = Path(settings.CONFIRMATION_MODEL_PATH)
    version = timezone.now().strftime("%Y%m%dT%H%M%S%fZ")
    artifact_path = configured_path.with_name(f"{configured_path.stem}-{version}{configured_path.suffix or '.joblib'}")
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": selected, "feature_version": FEATURE_VERSION, "classes": list(selected.classes_)}, artifact_path)

    with transaction.atomic():
        ModelVersion.objects.filter(active=True).update(active=False)
        model_version = ModelVersion.objects.create(
            name="RailSwift confirmation predictor",
            version=version,
            algorithm=algorithm,
            feature_version=FEATURE_VERSION,
            artifact_path=str(artifact_path),
            training_records=len(train_rows),
            journey_groups=len(train_groups | validation_groups),
            brier_score=metrics["brier_score"],
            log_loss=metrics["log_loss"],
            accuracy=metrics["accuracy"],
            active=True,
        )
    return model_version, metrics, len(groups)
