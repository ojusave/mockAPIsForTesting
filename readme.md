# Mock Zoom API

A mock API that mirrors [Zoom’s REST API](https://developers.zoom.us/docs/api/) for meetings, users, recordings, calendar, mail, chat, phone, and quality scoring. Uses random but realistic data and 2026-oriented defaults for testing and development.

**Base URL:** `https://zoom-test-apis.onrender.com` (or set `BASE_URL` in `.env`)

## Authentication

**This mock only:** All endpoints expect a `Bearer` token, and **this mock accepts any Bearer token value** so you can test without real credentials.

**Zoom’s real API:** Zoom does **not** accept arbitrary tokens. Production Zoom APIs require either:
- **OAuth 2.0** (user or server-to-server), or  
- **JWT** (legacy; signed with your Zoom app’s API Key and Secret).

Tokens must be obtained from Zoom (e.g. OAuth flow or JWT generation). See [Zoom Authentication](https://developers.zoom.us/docs/integrations/oauth/) and [Zoom API](https://developers.zoom.us/docs/api/).

For this mock, use any value for testing:

```http
Authorization: Bearer any-token-value
```

## Endpoint checks and Zoom alignment

**Smoke tests:** The following were exercised and return HTTP 200 (or 201/204 where applicable):

- `GET /users`, `GET /users/<user_id>`
- `GET /users/<user_id>/meetings?from=2026-01-01&to=2026-12-31`
- `GET /meetings/<meeting_id>`, `GET /meetings/<meeting_id>/meeting_summary`
- `GET /users/<user_id>/recordings`, `GET /meetings/<meeting_id>/recordings`
- `GET /qss/score/<meeting_id>`
- `GET /rec/download/<meeting_id>/transcript.vtt`

**Documented in Zoom’s API:** The following areas are covered in Zoom’s official docs ([developers.zoom.us](https://developers.zoom.us/docs/api/), base path `https://api.zoom.us/v2/`):

- **Users** – List/create/get/update/delete user, status, token, settings (e.g. virtual backgrounds).
- **Meetings** – List/create/get/update/delete meetings, meeting summary, past meeting participants.
- **Recordings** – List user recordings, list/delete meeting recordings (e.g. `GET /users/:userId/recordings`, `GET /meetings/:meetingId/recordings`).
- **Accounts** – Account-level settings (e.g. lock settings).
- **Zoom Phone** – Account settings, outbound caller ID, rooms, etc. (separate Zoom Phone API).
- **Zoom Chat** – Channels, messages, members (separate Chat API).

**Not part of Zoom’s REST API (mock-only / inspired by other products):**

- **Calendar** – The `/calendars/...` and event endpoints (e.g. `calendar#event`, ACL, freeBusy) follow a **Google Calendar–style** API, not Zoom’s calendar integration.
- **Mail** – The `/emails/mailboxes/...` (drafts, labels, threads, send) are **Gmail-style**; Zoom does not expose a general “Mail” REST API like this.
- **QSS / quality score** – Endpoints like `/qss/score`, `/qss/feedback`, and `/metrics/.../qos_summary` are **mock/conceptual** for testing; Zoom has reporting/dashboard and metrics APIs but the exact paths and shapes differ.

So: **Users, Meetings, Recordings, Past participants, Meeting summary, Accounts, Phone, and Chat** align with Zoom-documented concepts (paths may use or omit a `/v2` prefix in this mock). **Calendar, Mail, and the exact QSS paths** are not from Zoom’s docs and are for mock/testing only.

---

## Users (Zoom-style)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | List users (supports `page_size`, `page_number`) |
| POST | `/users` | Create user (body: `email`, `first_name`, `last_name`) |
| GET | `/users/<user_id>` | Get user |
| PATCH | `/users/<user_id>` | Update user |
| DELETE | `/users/<user_id>` | Delete user |
| PUT | `/users/<user_id>/status` | Update status (body: `action`: activate / deactivate) |
| GET | `/users/<user_id>/token` | Get user token/ZAK |
| DELETE | `/users/<user_id>/token` | Revoke SSO token |
| POST | `/users/<user_id>/settings/virtual_backgrounds` | Upload virtual background |
| DELETE | `/users/<user_id>/settings/virtual_backgrounds` | Delete virtual backgrounds |

---

## Meetings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/<user_id>/meetings` | List meetings (query: `from`, `to` — default 2026) |
| POST | `/users/<user_id>/meetings` | Create meeting |
| GET | `/meetings/<meeting_id>` | Get meeting by ID |
| GET | `/users/<user_id>/meetings/<meeting_id>` | Get meeting (with host) |
| PATCH | `/users/<user_id>/meetings/<meeting_id>` | Update meeting |
| DELETE | `/users/<user_id>/meetings/<meeting_id>` | Delete meeting |
| GET | `/meetings/<meeting_id>/meeting_summary` | Get meeting summary |
| GET | `/past_meetings/<meeting_id>/participants` | List past meeting participants |

---

## Recordings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/<user_id>/recordings` | List user recordings (`from`, `to`, `page_size`) |
| GET | `/meetings/<meeting_id>/recordings` | List recordings for a meeting |
| DELETE | `/meetings/<meeting_id>/recordings/<recording_id>` | Delete a recording |
| GET | `/rec/download/<meeting_id>/transcript.vtt` | Download VTT transcript |

---

## Quality Scoring (QSS)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/qss/score/<meeting_id>` | Get quality score for meeting |
| POST | `/qss/feedback` | Submit quality feedback |
| GET | `/qss/feedback/<feedback_id>` | Get feedback by ID |
| DELETE | `/qss/feedback/<feedback_id>` | Delete feedback |
| GET | `/metrics/meetings/<meeting_id>/participants/qos_summary` | Meeting QoS summary |
| GET | `/metrics/webinars/<webinar_id>/participants/qos_summary` | Webinar QoS summary |
| GET | `/videosdk/sessions/<session_id>/users/qos_summary` | Video SDK session QoS |

---

## Calendar

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/calendars/<cal_id>` | Get calendar |
| PATCH | `/calendars/<cal_id>` | Update calendar |
| DELETE | `/calendars/<cal_id>` | Delete calendar |
| POST | `/calendars` | Create calendar |
| GET | `/calendars/users/<user_id>/calendarList` | List user calendars |
| GET | `/calendars/<cal_id>/events` | List events |
| GET | `/calendars/<cal_id>/events/<event_id>` | Get event |
| POST | `/calendars/<cal_id>/events/import` | Import event |
| POST | `/calendars/<cal_id>/events/quickAdd` | Quick add (query: `text`) |
| DELETE | `/calendars/<cal_id>/events/<event_id>` | Delete event |
| POST | `/calendars/<cal_id>/events/<event_id>/move` | Move event (query: `destination`) |
| GET | `/calendars/<cal_id>/acl` | List ACL rules |
| POST | `/calendars/<cal_id>/acl` | Create ACL rule |
| GET | `/calendars/<cal_id>/acl/<acl_id>` | Get ACL rule |
| DELETE | `/calendars/<cal_id>/acl/<acl_id>` | Delete ACL rule |
| GET | `/calendars/colors` | Calendar/event colors |
| POST | `/calendars/freeBusy` | Query free/busy |

---

## Mail (emails)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/emails/mailboxes/<email>/drafts` | List drafts |
| GET | `/emails/mailboxes/<email>/labels` | List labels |
| GET | `/emails/mailboxes/<email>/threads` | List threads |
| POST | `/emails/mailboxes/<email>/messages/send` | Send message (body: `raw`, optional `sendTime`) |

---

## Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/chat/channels` | List channels |
| POST | `/chat/channels` | Create channel |
| GET | `/chat/channels/<channel_id>` | Get channel |
| PATCH | `/chat/channels/<channel_id>` | Update channel |
| DELETE | `/chat/channels/<channel_id>` | Delete channel |
| GET | `/chat/channels/<channel_id>/messages` | List messages |
| POST | `/chat/channels/<channel_id>/messages` | Send message |
| GET | `/chat/channels/<channel_id>/members` | List members |
| POST | `/chat/channels/<channel_id>/members` | Add members |
| DELETE | `/chat/channels/<channel_id>/members/<member_id>` | Remove member |
| POST | `/chat/channels/<channel_id>/members/me` | Join channel |
| DELETE | `/chat/channels/<channel_id>/members/me` | Leave channel |
| POST | `/chat/channels/search` | Search channels |
| GET | `/chat/users/<user_id>/messages` | List user messages |
| POST | `/chat/users/<user_id>/messages` | Send DM |
| GET/PUT/PATCH/DELETE | `/chat/users/<user_id>/messages/<message_id>` | Get/update/delete message |
| GET | `/chat/users/me/messages` | List my messages |
| GET/PUT/PATCH/DELETE | `/chat/users/me/messages/<message_id>` | My message |

---

## Phone (v2)

Prefix: `/v2/phone`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v2/phone/account_settings` | Account settings |
| GET | `/v2/phone/outbound_caller_id/customized_numbers` | Customized numbers |
| GET | `/v2/phone/outbound_caller_id/customized_numbers/<id>` | Get number |
| POST | `/v2/phone/outbound_caller_id/customized_numbers` | Add number |
| DELETE | `/v2/phone/outbound_caller_id/customized_numbers/<id>` | Delete number |
| GET/PATCH | `/v2/phone/call_live_transcription` | Live transcription |
| GET/PATCH | `/v2/phone/local_survivability_mode` | Local survivability |
| GET | `/v2/phone/alert_settings` | Alert settings |
| GET | `/v2/phone/voice_mails` | Voicemails |
| GET | `/v2/phone/rooms` | List Zoom Rooms |
| GET/POST/DELETE | `/v2/phone/rooms/<room_id>` | Get/create/delete room |
| POST/DELETE | `/v2/phone/rooms/<room_id>/calling_plans/...` | Calling plans |
| POST/DELETE | `/v2/phone/rooms/<room_id>/phone_numbers/...` | Room phone numbers |

---

## Accounts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/accounts/<accountId>/lock_settings` | Account lock settings |

---

## Sample requests (2026)

**Get user:**
```bash
curl -s -X GET "https://zoom-test-apis.onrender.com/users/abc123" \
  -H "Authorization: Bearer any-token"
```

**List meetings (2026 range):**
```bash
curl -s -X GET "https://zoom-test-apis.onrender.com/users/abc123/meetings?from=2026-01-01&to=2026-12-31" \
  -H "Authorization: Bearer any-token"
```

**Get meeting summary:**
```bash
curl -s -X GET "https://zoom-test-apis.onrender.com/meetings/meeting123/meeting_summary" \
  -H "Authorization: Bearer any-token"
```

**Error response (Zoom-style):**
```json
{
  "error": {
    "code": "404",
    "message": "Resource not found",
    "details": "The requested URL was not found"
  }
}
```

---

## Configuration

- **BASE_URL** – Used in response links (e.g. `join_url`, `download_url`). Default: `https://api.zoom.us`
- **DEFAULT_DATE_FROM / DEFAULT_DATE_TO** – Default list date range (e.g. 2026-01-01 to 2026-12-31)
- **DEFAULT_PAGE_SIZE / MAX_PAGE_SIZE** – Pagination (default 30, max 300)

See `config.py` and optional `.env`.

---

## Data structure (Zoom-style, file-backed)

API responses for **users**, **meetings**, **recordings**, **meeting summary**, **past participants**, and **VTT download** are derived from the `data/` directory. This mirrors Zoom’s account/user/meeting model.

| Path | Description |
|------|-------------|
| `data/accounts.json` | Zoom account list (e.g. account id, name, settings). |
| `data/users/<user_id>.json` | Full user profile (id, first_name, last_name, email, type, timezone, status, …). Optional: `meeting_ids[]`, `recording_meeting_ids[]` to link to meetings that have recordings. |
| `data/meetings/<meeting_id>.json` | Full meeting object (uuid, id, host_id, topic, type, start_time, duration, timezone, join_url, settings, …). Also: `summary` (title, overview, details, next_steps), `vtt_data` (transcript), `recording_files[]`, `participants[]`. |

- **GET /users**, **GET /users/:id** → from `data/users/`.
- **GET /users/:id/meetings** → meetings listed in the user’s `meeting_ids`, loaded from `data/meetings/`.
- **GET /meetings/:id**, **GET /meetings/:id/meeting_summary** → from `data/meetings/:id.json`.
- **GET /users/:id/recordings**, **GET /meetings/:id/recordings** → recording files and meeting metadata from the same meeting files.
- **GET /rec/download/:meeting_id/transcript.vtt** → VTT from `vtt_data` in `data/meetings/:id.json`.
- **GET /past_meetings/:id/participants** → `participants` array from `data/meetings/:id.json`.

Write operations (POST/PATCH/PUT/DELETE) may return success and update in-memory/cache only; persisting to these JSON files is optional and partially implemented (e.g. user PATCH merges into loaded user and can be extended to call `data_store.save_user`).

The legacy `files/` directory (meeting summaries only) is no longer used by the API; data was migrated into `data/meetings/` via `scripts/migrate_meetings_to_data.py`.

---

## Notes

- Core Zoom resources (users, meetings, recordings, summary, VTT, participants) are file-backed in `data/` and stable across restarts; other endpoints (calendar, mail, chat, phone, QSS) may use in-memory or random mock data.
- Any Bearer token is accepted; no rate limiting.
- Architecture: `config.py` (env/constants), `data_store.py` (load/save from `data/`), `helpers.py` (ids, dates, errors), `models/auth.py` (auth), `routes/*` (Zoom-aligned endpoints), VTT download in `app.py`.

For issues or contributions, open a GitHub issue.
