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

## Planned phases

1. Foundation and shared API connectivity (current)
2. Accounts, stations, train catalog, search, and saved journeys
3. Booking preparation and reminders
4. Historical waitlist data and train-wise analytics
5. Confirmation prediction and calibrated model reporting
6. Authorized PNR and chart integrations
7. Notifications, Android parity, and operational hardening
