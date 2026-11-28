# RailSwift

RailSwift is a railway journey planning and decision-support project. It prepares users for booking on the official railway site and will later add historical waitlist analytics and confirmation estimates. Ticket booking stays user-controlled.

## Phase 1: foundation

This phase establishes a shared Django API, a React web client, a Flutter Android client, and a local MySQL service. Both clients use the same versioned API at `/api/v1`.

### Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- Flutter SDK with Android tooling
- Docker Desktop with Compose

### Configure environment

Copy `.env.example` to `.env` and replace the Django secret before using the app beyond local development. The values in the example are development-only.

MySQL is the default database and runs through Docker Compose below. To run the API without Docker, set `DJANGO_DB_ENGINE=sqlite` in `.env`; the local database is stored in the ignored `db.sqlite3` file. Set it back to `mysql` when using the Compose database.

### Start MySQL

```powershell
docker compose up -d mysql
```

### Start the API

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

The API health endpoint is `http://127.0.0.1:8000/api/v1/health/`. It reports whether the API and configured database are reachable.

Load the clearly fictional sample timetable records after migrations:

```powershell
python manage.py load_demo_data
```

The web app can then search routes such as `ADI` to `MMCT`. All sample trains are labeled as demo records and are not live railway schedules.

### Start the web client

In another terminal:

```powershell
cd web
npm install
npm run dev
```

The web client reads `VITE_API_BASE_URL` from the root `.env`; it defaults to `http://127.0.0.1:8000/api/v1`.

### Start the Android client

After installing Flutter and Android tooling:

```powershell
cd android
flutter create . --project-name railswift --platforms android
flutter pub get
flutter run
```

The Android client defaults to `http://10.0.2.2:8000/api/v1` for the Android emulator. For a physical device, pass your development machine's LAN address with `--dart-define=API_BASE_URL=http://<host-ip>:8000/api/v1`.

Because local development uses HTTP, after generating the Android platform files, add `android:usesCleartextTraffic="true"` to the `<application>` element in `android/app/src/main/AndroidManifest.xml`. This setting is for local development; use HTTPS and remove the cleartext exception before production.

## Project map

```text
backend/  Django REST API and service modules
web/      React + TypeScript browser client
android/  Flutter Android client
docs/     Architecture, API, data, and development notes
```

## Data and booking boundaries

Live railway information must come from authorized or properly licensed sources. Sample or synthetic records must be labeled as such and must not be presented as real historical railway outcomes. RailSwift does not automate booking, bypass queues or CAPTCHA, or store railway credentials or payment details.

## Phases 3–6: planning, analytics, predictions, and railway data adapters

The API now includes booking plans and email reminders, privacy-conscious waitlist history import and coverage, a time-split calibrated confirmation model workflow, and interfaces for authorized PNR and reservation-chart providers. These features require migrations; run `python manage.py migrate` after installing backend dependencies.

Start the background workers in separate terminals after `docker compose up -d mysql redis`:

```powershell
cd backend
celery -A config worker -l info
```

```powershell
cd backend
celery -A config beat -l info
```

Booking plans and reminders are available at `/api/v1/booking-plans/`. Reminders use Django's configured email backend; the default prints email contents in the API process console. Configure SMTP before relying on delivery.

Historical waitlist imports are admin-only at `/api/v1/analytics/waitlist/import/`, or can be loaded from the command line with `python manage.py import_waitlist_csv <path>`. CSVs require the documented headers in [the data notes](docs/phase-3-6.md), and must not contain passenger or booking identifiers. Train a model with `python manage.py train_confirmation_model` after enough representative, deidentified history has been collected. The command requires at least 40 distinct journey groups spanning all supported outcome classes; it reserves the latest journeys for validation and final evaluation. Prediction endpoints return unavailable until a model is trained and registered. Versioned model files are written to the repository's ignored `ml_engine/models/` folder.

PNR numbers are encrypted at rest. Before adding trackers, set a generated Fernet key as `PNR_ENCRYPTION_KEY` and configure `RAILWAY_PROVIDER_CLASS` to an adapter you are authorized to use. A provider adapter must explicitly set `authorized = True` and implement the contract described in [the phase 3–6 notes](docs/phase-3-6.md). Without that adapter, PNR and chart endpoints return `503`; RailSwift does not scrape railway sites or bypass access controls. Do not change the encryption key after storing trackers unless you have securely migrated the ciphertexts.

## Roadmap

1. Foundation and shared API connectivity
2. Accounts, stations, train catalog, search, and saved journeys
3. Booking preparation and reminders (API and worker implemented)
4. Historical waitlist data and train-wise analytics (import and coverage API implemented)
5. Confirmation prediction and calibrated model reporting (training and prediction API implemented)
6. Authorized PNR and chart integration interfaces (secure storage and provider adapter contract implemented; live data depends on an authorized provider)
7. Web and Android feature parity, push delivery, and operational hardening
