# RailSwift phases 3–6

This note describes the shared Django APIs and operational requirements. No live railway provider is bundled or configured. Sample timetable data is fictional and is not used as waitlist training history.

## Phase 3: booking preparation and reminders

- `GET/POST /api/v1/booking-plans/` and standard detail/update/delete actions are scoped to the signed-in user.
- `POST /api/v1/booking-plans/{id}/reminders/` accepts `{"remind_at":"<ISO-8601 datetime>"}`.
- The Celery beat task sends due reminders through Django email and records delivery in `/api/v1/notifications/`.
- Booking remains a handoff to the official railway site. The app never submits a ticket order.

Run the worker and beat scheduler as separate processes. Configure a real email backend for delivery; the local default is Django's console backend.

## Phase 4: waitlist history

CSV import accepts these exact columns:

```text
journey_key,train_number,source_code,destination_code,journey_date,travel_class,quota,initial_waitlist,current_waitlist,days_remaining,final_outcome,captured_at,source_label
```

`source_label` is optional; all other columns are required. Reuse the same opaque UUID `journey_key` for rows from one journey to keep its observations grouped during training. Never use a PNR or passenger identifier as the key.

Allowed outcomes are `CNF`, `RAC`, and `WL`; classes and quotas are validated against the model choices. The importer rejects identifier-like headers (including PNR, passenger name, contact, and booking ID) and caps files at 5 MB and 10,000 rows. Use deidentified, licensed data and retain no passenger-level identifiers. Admins can import at `/api/v1/analytics/waitlist/import/`; the same importer is available via `python manage.py import_waitlist_csv <path>`.

## Phase 5: confirmation estimates

Run `python manage.py train_confirmation_model` after imports. Training requires at least 40 distinct journey groups and examples of all three outcomes. A chronological split reserves recent groups for validation and final evaluation. The command selects between calibrated logistic regression and calibrated random forest models using validation log loss, then reports accuracy, log loss, and multiclass Brier score on the held-out final period. Versioned artifacts are written under `ml_engine/models/` at the repository root (ignored by Git).

- `GET /api/v1/predictions/status/` reports whether a model is ready.
- `POST /api/v1/predictions/confirmation/` accepts train, segment, date, class, quota, waitlist, and days-remaining features.
- `GET /api/v1/predictions/history/` returns the signed-in user's last 50 estimates.
- `GET /api/v1/predictions/metrics/` is admin-only.

Every estimate is labeled as historical decision support, with probability and confidence outputs. It is not a guarantee of confirmation.

## Phase 6: authorized PNR and chart provider contract

Set `PNR_ENCRYPTION_KEY` to a fresh key produced by `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. Store it in a secret manager or local `.env`, never commit it, and keep a protected backup. The key is also used to derive a keyed PNR fingerprint for per-user duplicate detection. API responses reveal only a masked PNR.

Implement an adapter subclassing `integrations.base.RailwayDataProvider`, set `authorized = True` only after approval for that data source, and configure `RAILWAY_PROVIDER_CLASS` to its dotted import path. `get_pnr_status(pnr)` returns a dictionary with a `status` such as `waitlisted`, `confirmed`, `cancelled`, or `chart_prepared`. `get_chart(train_number, journey_date)` returns a dictionary shaped like:

```json
{
  "status": "first_prepared",
  "class_code": "SL",
  "coaches": [
    {
      "coach_number": "S1",
      "class_code": "SL",
      "from_station": "ADI",
      "to_station": "MMCT",
      "vacant_count": 2,
      "occupied_count": 70
    }
  ]
}
```

The tracker API is `GET/POST /api/v1/pnr-trackers/`, `DELETE /api/v1/pnr-trackers/{id}/`, and `POST /api/v1/pnr-trackers/{id}/check/`. It is user-scoped and requires both an authorized adapter and encryption key for creation. The scheduled worker checks active records every 15 minutes. Chart snapshots are fetched by authenticated `GET /api/v1/charts/?train_number=<number>&journey_date=YYYY-MM-DD`; persisted results can be fetched at `/api/v1/charts/{snapshot_id}/`.

Without a configured, authorized adapter these live endpoints return `503`. The repository intentionally contains no scraping adapter, railway account credential handling, or CAPTCHA/queue bypass.
