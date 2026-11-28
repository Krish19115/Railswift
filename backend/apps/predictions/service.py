from pathlib import Path

import joblib
import pandas as pd
from django.conf import settings
from django.db.models import Count

from apps.historical.models import WaitlistObservation
from .models import ModelVersion


class ModelUnavailable(Exception):
    pass


def model_status():
    return ModelVersion.objects.filter(active=True).first()


def predict(data):
    version = model_status()
    if not version:
        raise ModelUnavailable("No confirmation model is active. Import enough historical data and train a model first.")
    artifact = Path(version.artifact_path)
    if not artifact.exists():
        raise ModelUnavailable("The active model artifact is missing. Retrain or restore the model artifact.")
    try:
        bundle = joblib.load(artifact)
    except (OSError, ValueError, EOFError) as exc:
        raise ModelUnavailable("The active model artifact could not be loaded.") from exc
    if bundle.get("feature_version") != version.feature_version:
        raise ModelUnavailable("The model feature version is not supported by this API.")

    features = pd.DataFrame([{
        "train_number": data["train"].number,
        "source_code": data["source_station"].code,
        "destination_code": data["destination_station"].code,
        "travel_class": data["travel_class"],
        "quota": data["quota"],
        "initial_waitlist": data["initial_waitlist"],
        "current_waitlist": data["current_waitlist"],
        "days_remaining": data["days_remaining"],
        "wl_movement": data["initial_waitlist"] - data["current_waitlist"],
    }])
    model = bundle["model"]
    probabilities = model.predict_proba(features)[0]
    outcomes = {name: float(probability) for name, probability in zip(model.classes_, probabilities)}
    comparable = WaitlistObservation.objects.filter(
        train=data["train"], source_station=data["source_station"], destination_station=data["destination_station"],
        travel_class=data["travel_class"], quota=data["quota"],
    ).values("journey_key").distinct().count()
    confidence = "high" if comparable >= 500 else "medium" if comparable >= 100 else "low"
    return {
        "model_version": version,
        "probabilities": {"confirmed": outcomes.get("CNF", 0.0), "rac": outcomes.get("RAC", 0.0), "waitlisted": outcomes.get("WL", 0.0)},
        "confidence": confidence,
        "comparable_journeys": comparable,
    }
