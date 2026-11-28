import csv
import uuid
from datetime import date, datetime

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from apps.stations.models import Station
from apps.trains.models import Train, TrainStop
from .models import WaitlistObservation

REQUIRED_COLUMNS = {
    "journey_key", "train_number", "source_code", "destination_code", "journey_date",
    "travel_class", "quota", "initial_waitlist", "current_waitlist", "days_remaining",
    "final_outcome", "captured_at",
}
FORBIDDEN_HEADER_PARTS = ("pnr", "passenger", "phone", "email", "address", "name", "booking_id")


def validate_headers(headers):
    normalized = {item.strip().lower() for item in headers if item}
    forbidden = sorted(name for name in normalized if any(part in name for part in FORBIDDEN_HEADER_PARTS))
    if forbidden:
        raise ValueError("Personal identifiers are not accepted in historical training data.")
    missing = sorted(REQUIRED_COLUMNS - normalized)
    if missing:
        raise ValueError(f"Missing required CSV columns: {', '.join(missing)}")


def observation_from_row(row):
    row = {key.strip().lower(): (value or "").strip() for key, value in row.items() if key}
    journey_key = uuid.UUID(row["journey_key"])
    train = Train.objects.get(number=row["train_number"].upper(), is_active=True)
    source = Station.objects.get(code=row["source_code"].upper(), is_active=True)
    destination = Station.objects.get(code=row["destination_code"].upper(), is_active=True)
    journey_date = date.fromisoformat(row["journey_date"])
    captured_at = datetime.fromisoformat(row["captured_at"].replace("Z", "+00:00"))
    if timezone.is_naive(captured_at):
        captured_at = timezone.make_aware(captured_at, timezone.get_current_timezone())
    observation = WaitlistObservation(
        journey_key=journey_key,
        train=train,
        source_station=source,
        destination_station=destination,
        journey_date=journey_date,
        travel_class=row["travel_class"].upper(),
        quota=row["quota"].upper(),
        initial_waitlist=int(row["initial_waitlist"]),
        current_waitlist=int(row["current_waitlist"]),
        days_remaining=int(row["days_remaining"]),
        final_outcome=row["final_outcome"].upper(),
        captured_at=captured_at,
        source_label=row.get("source_label", "")[:80],
    )
    observation.full_clean(exclude=("id",))
    if source.pk == destination.pk:
        raise ValueError("Origin and destination must differ.")
    source_stop = TrainStop.objects.filter(train=train, station=source).values_list("stop_order", flat=True).first()
    destination_stop = TrainStop.objects.filter(train=train, station=destination).values_list("stop_order", flat=True).first()
    if source_stop is None or destination_stop is None or destination_stop <= source_stop:
        raise ValueError("Origin and destination must be a forward segment on the selected train.")
    return observation


def import_csv_file(file_obj, max_rows=10000):
    try:
        text = file_obj.read().decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Upload must be a UTF-8 encoded CSV file.") from exc
    reader = csv.DictReader(text.splitlines())
    validate_headers(reader.fieldnames or [])
    records = []
    for line_number, row in enumerate(reader, start=2):
        if line_number > max_rows + 1:
            raise ValueError(f"CSV exceeds the {max_rows} row limit.")
        try:
            records.append(observation_from_row(row))
        except (KeyError, ValueError, TypeError, Train.DoesNotExist, Station.DoesNotExist, DjangoValidationError) as exc:
            detail = "; ".join(exc.messages) if isinstance(exc, DjangoValidationError) else str(exc)
            raise ValueError(f"Row {line_number}: {detail}") from exc
    if not records:
        raise ValueError("CSV contains no data rows.")
    WaitlistObservation.objects.bulk_create(records, batch_size=500)
    return len(records)
