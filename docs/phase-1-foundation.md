# Phase 1: Foundation

## Scope

- Django REST Framework API with a shared `/api/v1/` prefix.
- React + TypeScript web client and Flutter Android client.
- MySQL 8.4 local development service.
- A health endpoint that reports application and database reachability.
- Shared API base URL conventions for both clients.

## Architecture

```text
React web client ───┐
                    ├── Django REST API (/api/v1/) ─── MySQL
Flutter Android ────┘
```

The clients do not connect directly to MySQL. The API defaults to authenticated access; public endpoints must opt into public access explicitly. The health endpoint is public so both clients can show service connectivity before sign-in exists.

## Health contract

`GET /api/v1/health/`

Healthy response (`200`):

```json
{ "status": "ok", "database": "ok" }
```

Database unavailable (`503`):

```json
{ "status": "degraded", "database": "unavailable" }
```

## Local configuration

The repository root `.env.example` is the starting point for local settings. The API should bind to `0.0.0.0:8000` for Android emulator access, and the allowed-host list includes the emulator's `10.0.2.2` address. The React Vite config loads that root environment file. Flutter reads `API_BASE_URL` through a Dart compile-time define; the default address targets the Android emulator, and a physical device needs a reachable host LAN address. Android's development manifest must allow cleartext traffic for the local HTTP endpoint; remove that exception when using HTTPS in production.

The Compose database credentials and Django secret are development placeholders. Replace them before exposing any service beyond a local development machine.

## Deferred to later phases

Accounts, train/station data models, search, booking plans, prediction models, PNR/chart integrations, and notification delivery belong to later phases. Railway data adapters must use authorized or licensed sources. Booking submission remains on the official railway platform and user-controlled.
