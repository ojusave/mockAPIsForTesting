# Mock Zoom API

A mock API that mirrors Zoom-style REST endpoints for meetings, users, recordings, webinars, chat, phone, and related resources. All data is stored in the `data/` folder (single source of truth).

**Base URL:** Set `BASE_URL` in `.env` (e.g. your deployed URL or `https://api.zoom.us`). All routes are under the `/v2` prefix.

## Authentication

Send a `Bearer` value in the `Authorization` header. Any value is accepted.

```http
Authorization: Bearer any-value
```

## Endpoints

All paths are prefixed with `/v2` (e.g. `/v2/users`, `/v2/meetings/<id>`).

### Users

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v2/users` | List users (`page_size`, `page_number`, `status`) |
| POST | `/v2/users` | Create user (`email`, `first_name`, `last_name`) |
| GET | `/v2/users/me` | Current user |
| GET | `/v2/users/<user_id>` | Get user |
| PATCH | `/v2/users/<user_id>` | Update user |
| DELETE | `/v2/users/<user_id>` | Delete user |
| PUT | `/v2/users/<user_id>/status` | Update status (`action`: activate / deactivate) |
| GET/PATCH | `/v2/users/<user_id>/settings` | User settings |
| POST/DELETE | `/v2/users/<user_id>/settings/virtual_backgrounds` | Virtual backgrounds |

### Meetings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v2/users/<user_id>/meetings` | List meetings (`from`, `to`, `page_size`) |
| POST | `/v2/users/<user_id>/meetings` | Create meeting |
| GET | `/v2/meetings/<meeting_id>` | Get meeting |
| GET | `/v2/users/<user_id>/meetings/<meeting_id>` | Get meeting (with host) |
| PATCH | `/v2/users/<user_id>/meetings/<meeting_id>` | Update meeting |
| DELETE | `/v2/users/<user_id>/meetings/<meeting_id>` | Delete meeting |
| GET | `/v2/meetings/<meeting_id>/meeting_summary` | Meeting summary |
| GET | `/v2/past_meetings/<meeting_id>/participants` | Past meeting participants |

### Recordings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v2/users/<user_id>/recordings` | List user recordings |
| GET | `/v2/meetings/<meeting_id>/recordings` | List meeting recordings |
| DELETE | `/v2/meetings/<meeting_id>/recordings/<recording_id>` | Delete recording |
| GET | `/v2/rec/download/<meeting_id>/transcript.vtt` | Download VTT transcript |

### Webinars

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v2/users/<user_id>/webinars` | List webinars |
| POST | `/v2/users/<user_id>/webinars` | Create webinar |
| GET | `/v2/webinars/<webinar_id>` | Get webinar |
| PATCH/DELETE | `/v2/users/<user_id>/webinars/<webinar_id>` | Update / delete webinar |
| GET | `/v2/past_webinars/<webinar_id>/participants` | Past webinar participants |

### Reports & metrics

| Method | Path |
|--------|------|
| GET | `/v2/report/users` |
| GET | `/v2/report/meetings/<meeting_id>/participants` |
| GET | `/v2/report/webinars/<webinar_id>/participants` |
| GET | `/v2/metrics/meetings` |
| GET | `/v2/metrics/meetings/<meeting_id>/participants` |
| GET | `/v2/metrics/webinars/<webinar_id>/participants` |

### QSS (quality scoring)

| Method | Path |
|--------|------|
| GET | `/v2/qss/score/<meeting_id>` |
| POST | `/v2/qss/feedback` |
| GET | `/v2/qss/feedback/<feedback_id>` |
| DELETE | `/v2/qss/feedback/<feedback_id>` |
| GET | `/v2/metrics/meetings/<meeting_id>/participants/qos_summary` |

### Chat, calendar, mail, phone, devices, roles, groups, accounts, rooms, tracking fields

- **Chat:** `/v2/chat/channels`, `/v2/chat/channels/<id>/messages`, etc.
- **Calendar:** `/v2/calendars`, `/v2/calendars/<id>/events`, `/v2/calendars/freeBusy`, etc.
- **Mail:** `/v2/emails/mailboxes/<email>/drafts`, `/v2/emails/mailboxes/<email>/messages/send`, etc.
- **Phone:** `/v2/phone/account_settings`, `/v2/phone/rooms`, etc.
- **Devices:** `/v2/devices`, **Roles:** `/v2/roles`, **Groups:** `/v2/groups`
- **Accounts:** `/v2/accounts/<accountId>/lock_settings`
- **Rooms:** `/v2/rooms` (Zoom Rooms, not Phone rooms)
- **Tracking fields:** `/v2/tracking_fields`

## Sample requests

Replace `<user_id>`, `<meeting_id>` with IDs that exist in your `data/` (e.g. from `GET /v2/users` or `GET /v2/users/<user_id>/meetings`).

```bash
curl -s -X GET "http://localhost:8000/v2/users/<user_id>" \
  -H "Authorization: Bearer any-value"

curl -s -X GET "http://localhost:8000/v2/users/<user_id>/meetings?from=2026-01-01&to=2026-12-31" \
  -H "Authorization: Bearer any-value"

curl -s -X GET "http://localhost:8000/v2/meetings/<meeting_id>/meeting_summary" \
  -H "Authorization: Bearer any-value"
```

## Data (source of truth: `data/`)

All persistent data is read from and written to the `data/` directory:

| Path | Description |
|------|-------------|
| `data/accounts.json` | Account list |
| `data/users/<id>.json` | User profile; optional `meeting_ids`, `recording_meeting_ids`, `webinar_ids` |
| `data/meetings/<id>.json` | Meeting + `summary`, `vtt_data`, `recording_files`, `participants` |
| `data/webinars/<id>.json` | Webinar + `participants` |
| `data/tracking_fields.json` | Tracking fields list |
| `data/rooms.json` | Zoom Rooms list |
| `data/chat_channels.json` | Chat channels |
| `data/chat_messages.json` | Chat messages by channel |
| `data/qss_feedback.json` | QSS feedback entries |

## Configuration

- **BASE_URL** – Used in response links (e.g. `join_url`). Default: `https://api.zoom.us`
- **DEFAULT_DATE_FROM / DEFAULT_DATE_TO** – Default list date range (e.g. 2026-01-01 to 2026-12-31)
- **DEFAULT_PAGE_SIZE / MAX_PAGE_SIZE** – Pagination (default 30, max 300)

See `config.py` and optional `.env`.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Server runs at `http://0.0.0.0:8000` (or set port via env).
