# Phase 2 API

All paths use the `/api/v1/` prefix. JSON errors use DRF's standard validation response shape. Timetable search and catalog endpoints are public for the demo; account and saved-journey endpoints require a bearer access token.

## Authentication

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| POST | `/auth/register/` | Public | Create a username/email/password account; returns access and refresh JWTs |
| POST | `/auth/login/` | Public | Obtain JWTs using username or email and password |
| POST | `/auth/refresh/` | Refresh token | Rotate the refresh token and issue a new access token |
| POST | `/auth/logout/` | Access token | Blacklist the submitted refresh token |
| GET/PATCH | `/auth/profile/` | Access token | Read or update the current account email |

Send protected requests with `Authorization: Bearer <access-token>`.

## Stations and trains

| Method | Path | Query/body | Purpose |
| --- | --- | --- | --- |
| GET | `/stations/` | `search=<text>` | Search station code, name, or city |
| GET | `/trains/` | `search=<text>` | Search the train catalog |
| GET | `/trains/between/` | `from=<code>&to=<code>&date=YYYY-MM-DD` | Find scheduled sample train segments |
| GET | `/trains/{number}/` | — | Train details and ordered stops |
| GET | `/trains/{number}/schedule/` | — | Train schedule |

Train search returns schedule times and duration. It does not return live availability, fares, or confirmation predictions. The current seed uses fictional `RS` trains and marks responses as sample data.

## Saved journeys

| Method | Path | Purpose |
| --- | --- | --- |
| GET/POST | `/saved-journeys/` | List or save a user's route |
| GET/PATCH/DELETE | `/saved-journeys/{id}/` | Read, update, or remove a route owned by the current user |

Create body:

```json
{
  "source_code": "ADI",
  "destination_code": "MMCT",
  "journey_date": "2026-12-15",
  "preferred_class": "SL",
  "quota": "GN"
}
```

The API scopes list, detail, update, and delete operations to the authenticated user.
