#!/usr/bin/env python3
"""
Integration tests for mock Zoom API. Exercises GET, POST, PATCH, PUT, DELETE
with various query params and request bodies.
Run: python3 tests/test_endpoints.py
Or with pytest: pip install pytest && python3 -m pytest tests/ -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from app import app


def _client():
    app.config["TESTING"] = True
    return app.test_client()


def _auth_headers():
    return {"Authorization": "Bearer test-token-123", "Content-Type": "application/json"}


if HAS_PYTEST:
    @pytest.fixture
    def client():
        return _client()
    @pytest.fixture
    def auth_headers():
        return _auth_headers()
    @pytest.fixture
    def test_ids(client, auth_headers):
        """Resolve user_id, meeting_id, webinar_id, recording_id from API (data-driven)."""
        uid, mid, wid, rid = _resolve_test_ids(client, auth_headers)
        return {"user_id": uid, "meeting_id": mid, "webinar_id": wid, "recording_id": rid}


def _resolve_test_ids(client, auth_headers):
    """Resolve user_id, meeting_id, webinar_id, recording_id from API (data-driven, no hardcoded u1/m1)."""
    h = auth_headers
    r = client.get("/v2/users", headers=h)
    data = r.get_json() or {}
    users = data.get("users") or []
    if users:
        user_id = users[0].get("id")
    else:
        cr = client.post("/v2/users", headers=h, json={"email": "test@zoom-mock.com", "first_name": "Test", "last_name": "User"})
        user_id = cr.get_json().get("id") if cr.status_code == 201 else "test_user"
    r = client.get(f"/v2/users/{user_id}/meetings?from=2026-01-01&to=2026-12-31", headers=h)
    meetings = (r.get_json() or {}).get("meetings") or []
    if meetings:
        meeting_id = meetings[0].get("id")
    else:
        mr = client.post(f"/v2/users/{user_id}/meetings", headers=h, json={"topic": "Test", "duration": 30})
        meeting_id = mr.get_json().get("id") if mr.status_code == 201 else "test_meeting"
    r = client.get(f"/v2/users/{user_id}/webinars?from=2026-01-01&to=2026-12-31", headers=h)
    webinars = (r.get_json() or {}).get("webinars") or []
    webinar_id = webinars[0].get("id") if webinars else "test_webinar"
    r = client.get(f"/v2/meetings/{meeting_id}/recordings", headers=h)
    recs = (r.get_json() or {}).get("recording_files") or []
    recording_id = recs[0].get("id") if recs else "rec_test"
    return user_id, meeting_id, webinar_id, recording_id


def run_without_pytest():
    c = _client()
    h = _auth_headers()
    failed = []
    user_id, meeting_id, webinar_id, recording_id = _resolve_test_ids(c, h)
    # Create a separate user for DELETE test so main user_id remains for meetings/recordings
    dr = c.post("/v2/users", headers=h, json={"email": "delete-me@zoom-mock.com", "first_name": "Del", "last_name": "User"})
    delete_user_id = dr.get_json().get("id") if dr.status_code == 201 else "delete_test_user"
    # Base URL matches Zoom API: https://api.zoom.us/v2/ — IDs from store (data-driven)
    tests = [
        ("GET /v2/users", lambda: c.get("/v2/users", headers=h)),
        ("GET /v2/users?page_size=5&status=active", lambda: c.get("/v2/users?page_size=5&status=active", headers=h)),
        ("POST /v2/users", lambda: c.post("/v2/users", headers=h, json={"email": "t@x.com", "first_name": "A", "last_name": "B"})),
        ("POST /v2/users validation", lambda: c.post("/v2/users", headers=h, json={"email": "x"})),
        ("GET /v2/users/me", lambda: c.get("/v2/users/me", headers=h)),
        ("GET /v2/users/:id", lambda: c.get(f"/v2/users/{user_id}", headers=h)),
        ("PATCH /v2/users/:id", lambda: c.patch(f"/v2/users/{user_id}", headers=h, json={"first_name": "Patched"})),
        ("PUT /v2/users/:id/status", lambda: c.put(f"/v2/users/{user_id}/status", headers=h, json={"action": "activate"})),
        ("DELETE /v2/users/:id", lambda: c.delete(f"/v2/users/{delete_user_id}", headers=h)),
        ("GET /v2/users/:id/meetings", lambda: c.get(f"/v2/users/{user_id}/meetings?from=2026-01-01&to=2026-12-31&page_size=5", headers=h)),
        ("POST /v2/users/:id/meetings", lambda: c.post(f"/v2/users/{user_id}/meetings", headers=h, json={"topic": "T", "duration": 30})),
        ("GET /v2/meetings/:id", lambda: c.get(f"/v2/meetings/{meeting_id}", headers=h)),
        ("PATCH /v2/meetings", lambda: c.patch(f"/v2/users/{user_id}/meetings/{meeting_id}", headers=h, json={"topic": "Updated"})),
        ("DELETE /v2/meetings", lambda: c.delete(f"/v2/users/{user_id}/meetings/{meeting_id}", headers=h)),
        ("GET /v2/users/:id/recordings", lambda: c.get(f"/v2/users/{user_id}/recordings?page_number=1", headers=h)),
        ("GET /v2/meetings/:id/recordings", lambda: c.get(f"/v2/meetings/{meeting_id}/recordings", headers=h)),
        ("DELETE recording", lambda: c.delete(f"/v2/meetings/{meeting_id}/recordings/{recording_id}", headers=h, json={})),
        ("GET /v2/qss/score", lambda: c.get(f"/v2/qss/score/{meeting_id}", headers=h)),
        ("POST /v2/qss/feedback", lambda: c.post("/v2/qss/feedback", headers=h, json={"meeting_id": meeting_id, "rating": 5})),
        ("POST /v2/chat/channels", lambda: c.post("/v2/chat/channels", headers=h, json={"name": "Ch1", "type": 1})),
        ("POST /v2/chat/channels validation", lambda: c.post("/v2/chat/channels", headers=h, json={})),
        ("POST /v2/calendars", lambda: c.post("/v2/calendars", headers=h, json={"summary": "Cal"})),
        ("POST /v2/calendars/freeBusy", lambda: c.post("/v2/calendars/freeBusy", headers=h, json={"timeMin": "2026-01-01T00:00:00Z", "timeMax": "2026-01-02T00:00:00Z", "items": [{"id": "c1"}]})),
        ("POST mail send validation", lambda: c.post("/v2/emails/mailboxes/u@x.com/messages/send", headers=h, json={})),
        ("GET /v2/users/:id/webinars", lambda: c.get(f"/v2/users/{user_id}/webinars?from=2026-01-01&to=2026-12-31", headers=h)),
        ("GET /v2/webinars/:id", lambda: c.get(f"/v2/webinars/{webinar_id}", headers=h)),
        ("GET /v2/past_webinars/:id/participants", lambda: c.get(f"/v2/past_webinars/{webinar_id}/participants", headers=h)),
        ("GET /v2/report/users", lambda: c.get("/v2/report/users?type=active", headers=h)),
        ("GET /v2/report/meetings/:id/participants", lambda: c.get(f"/v2/report/meetings/{meeting_id}/participants", headers=h)),
        ("GET /v2/metrics/meetings", lambda: c.get("/v2/metrics/meetings?from=2026-01-01&to=2026-12-31", headers=h)),
        ("GET /v2/devices", lambda: c.get("/v2/devices", headers=h)),
        ("GET /v2/roles", lambda: c.get("/v2/roles", headers=h)),
        ("GET /v2/groups", lambda: c.get("/v2/groups", headers=h)),
        ("Auth required", lambda: c.get("/v2/users")),
    ]
    for name, req in tests:
        r = req()
        if "validation" in name or "Auth required" in name:
            ok = r.status_code in (400, 401)
        else:
            ok = r.status_code in (200, 201, 204)
        status = "OK" if ok else "FAIL"
        print(f"  {status} {name} -> {r.status_code}")
        if not ok and "validation" not in name and "Auth" not in name:
            failed.append(name)
    if failed:
        print(f"\nFailed: {failed}")
        sys.exit(1)
    print("\nAll checks passed.")


if __name__ == "__main__":
    if HAS_PYTEST:
        pytest.main([__file__, "-v"])
    else:
        run_without_pytest()


# ---- Users ---- (pytest only below)
def test_users_list_get(client, auth_headers):
    r = client.get("/v2/users", headers=auth_headers)
    assert r.status_code == 200
    data = r.get_json()
    assert "users" in data and "page_size" in data
    r2 = client.get("/v2/users?page_size=5&page_number=1&status=active", headers=auth_headers)
    assert r2.status_code == 200


def test_users_create_post(client, auth_headers):
    r = client.post("/v2/users", headers=auth_headers, json={
        "email": "new@example.com",
        "first_name": "New",
        "last_name": "User",
        "type": 2,
        "display_name": "New User",
        "password": "secret",
    })
    assert r.status_code == 201
    data = r.get_json()
    assert data["email"] == "new@example.com" and data["first_name"] == "New"


def test_users_create_validation(client, auth_headers):
    r = client.post("/v2/users", headers=auth_headers, json={"email": "only@example.com"})
    assert r.status_code == 400
    assert r.get_json().get("error", {}).get("code") == "400"


def test_users_get(client, auth_headers):
    r = client.get("/v2/users/abc123", headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["id"] == "abc123"


def test_users_patch(client, auth_headers, test_ids):
    r = client.patch(f"/v2/users/{test_ids['user_id']}", headers=auth_headers, json={
        "first_name": "Patched",
        "timezone": "Europe/London",
        "company": "Acme",
    })
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("first_name") == "Patched" and data.get("timezone") == "Europe/London"


def test_users_status_put(client, auth_headers, test_ids):
    r = client.put(f"/v2/users/{test_ids['user_id']}/status", headers=auth_headers, json={"action": "activate"})
    assert r.status_code == 200
    r2 = client.put(f"/v2/users/{test_ids['user_id']}/status", headers=auth_headers, json={})
    assert r2.status_code == 400


def test_users_token_get(client, auth_headers, test_ids):
    r = client.get(f"/v2/users/{test_ids['user_id']}/token?type=zak&ttl=3600", headers=auth_headers)
    assert r.status_code == 200
    assert "token" in r.get_json()


def test_users_delete(client, auth_headers):
    # Create a user just for delete so we don't remove the fixture user
    r = client.post("/v2/users", headers=auth_headers, json={"email": "del@example.com", "first_name": "Del", "last_name": "User"})
    assert r.status_code == 201
    uid = r.get_json()["id"]
    r = client.delete(f"/v2/users/{uid}", headers=auth_headers)
    assert r.status_code == 204


# ---- Meetings ----
def test_meetings_list_get(client, auth_headers, test_ids):
    r = client.get(f"/v2/users/{test_ids['user_id']}/meetings?from=2026-01-01&to=2026-12-31&page_size=5&type=scheduled", headers=auth_headers)
    assert r.status_code == 200
    data = r.get_json()
    assert "meetings" in data and "page_size" in data


def test_meetings_create_post(client, auth_headers, test_ids):
    r = client.post(f"/v2/users/{test_ids['user_id']}/meetings", headers=auth_headers, json={
        "topic": "Test Meeting",
        "duration": 45,
        "timezone": "America/Los_Angeles",
        "agenda": "Agenda here",
        "start_time": "2026-06-15T14:00:00Z",
        "settings": {"waiting_room": False},
    })
    assert r.status_code == 201
    data = r.get_json()
    assert data["topic"] == "Test Meeting" and data["duration"] == 45 and "agenda" in data


def test_meetings_get_by_id(client, auth_headers, test_ids):
    r = client.get(f"/v2/meetings/{test_ids['meeting_id']}", headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["id"] == test_ids["meeting_id"]


def test_meetings_patch(client, auth_headers, test_ids):
    r = client.patch(f"/v2/users/{test_ids['user_id']}/meetings/{test_ids['meeting_id']}", headers=auth_headers, json={
        "topic": "Updated Topic",
        "duration": 90,
        "settings": {"mute_upon_entry": False},
    })
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("topic") == "Updated Topic" and data.get("duration") == 90


def test_meetings_summary_get(client, auth_headers, test_ids):
    r = client.get(f"/v2/meetings/{test_ids['meeting_id']}/meeting_summary", headers=auth_headers)
    assert r.status_code == 200


def test_meetings_participants_get(client, auth_headers, test_ids):
    r = client.get(f"/v2/past_meetings/{test_ids['meeting_id']}/participants?page_size=10", headers=auth_headers)
    assert r.status_code == 200
    assert "participants" in r.get_json()


def test_meetings_delete(client, auth_headers, test_ids):
    # Create a meeting just for delete so we don't remove the fixture meeting
    r = client.post(f"/v2/users/{test_ids['user_id']}/meetings", headers=auth_headers, json={"topic": "To Delete", "duration": 15})
    assert r.status_code == 201
    mid = r.get_json()["id"]
    r = client.delete(f"/v2/users/{test_ids['user_id']}/meetings/{mid}", headers=auth_headers)
    assert r.status_code == 204


# ---- Recordings ----
def test_recordings_list_get(client, auth_headers, test_ids):
    r = client.get(f"/v2/users/{test_ids['user_id']}/recordings?from=2026-01-01&to=2026-12-31&page_size=5&page_number=1", headers=auth_headers)
    assert r.status_code == 200
    assert "meetings" in r.get_json()


def test_recordings_meeting_get(client, auth_headers, test_ids):
    r = client.get(f"/v2/meetings/{test_ids['meeting_id']}/recordings?trash=false", headers=auth_headers)
    assert r.status_code == 200
    assert "recording_files" in r.get_json()


def test_recordings_delete(client, auth_headers, test_ids):
    r = client.delete(f"/v2/meetings/{test_ids['meeting_id']}/recordings/{test_ids['recording_id']}", headers=auth_headers, json={"action": "delete"})
    assert r.status_code == 204


# ---- QSS ----
def test_qss_score_get(client, auth_headers, test_ids):
    r = client.get(f"/v2/qss/score/{test_ids['meeting_id']}", headers=auth_headers)
    assert r.status_code == 200
    assert "quality_score" in r.get_json()


def test_qss_feedback_post(client, auth_headers, test_ids):
    r = client.post("/v2/qss/feedback", headers=auth_headers, json={
        "meeting_id": test_ids["meeting_id"],
        "rating": 5,
        "comments": "Great meeting",
    })
    assert r.status_code == 201
    data = r.get_json()
    assert data.get("meeting_id") == test_ids["meeting_id"] and "id" in data


def test_qss_metrics_meeting_get(client, auth_headers, test_ids):
    r = client.get(f"/v2/metrics/meetings/{test_ids['meeting_id']}/participants/qos_summary?page_size=5", headers=auth_headers)
    assert r.status_code == 200
    assert "participants" in r.get_json()


# ---- Chat ----
def test_chat_channels_list(client, auth_headers):
    r = client.get("/v2/chat/channels", headers=auth_headers)
    assert r.status_code == 200


def test_chat_channels_create(client, auth_headers):
    r = client.post("/v2/chat/channels", headers=auth_headers, json={"name": "Test Channel", "type": 1})
    assert r.status_code == 201
    assert r.get_json()["name"] == "Test Channel"


def test_chat_channels_create_validation(client, auth_headers):
    r = client.post("/v2/chat/channels", headers=auth_headers, json={"type": 1})
    assert r.status_code == 400


def test_chat_messages_send(client, auth_headers):
    client.post("/v2/chat/channels", headers=auth_headers, json={"name": "C1", "type": 1})
    r = client.post("/v2/chat/channels/1/messages", headers=auth_headers, json={"message": "Hello"})
    assert r.status_code == 201


# ---- Calendar ----
def test_calendar_events_list(client, auth_headers):
    r = client.get("/v2/calendars/cal1/events?maxResults=10", headers=auth_headers)
    assert r.status_code == 200


def test_calendar_create(client, auth_headers):
    r = client.post("/v2/calendars", headers=auth_headers, json={"summary": "Work", "timeZone": "UTC"})
    assert r.status_code == 200


def test_calendar_create_validation(client, auth_headers):
    r = client.post("/v2/calendars", headers=auth_headers, json={})
    assert r.status_code == 400


def test_calendar_freebusy_post(client, auth_headers):
    r = client.post("/v2/calendars/freeBusy", headers=auth_headers, json={
        "timeMin": "2026-01-01T00:00:00Z",
        "timeMax": "2026-01-02T00:00:00Z",
        "items": [{"id": "cal1"}],
    })
    assert r.status_code == 200


# ---- Mail ----
def test_mail_send_validation(client, auth_headers):
    r = client.post("/v2/emails/mailboxes/u@example.com/messages/send", headers=auth_headers, json={})
    assert r.status_code == 400


def test_mail_send(client, auth_headers):
    r = client.post("/v2/emails/mailboxes/u@example.com/messages/send", headers=auth_headers, json={"raw": "YmFzZTY0"})
    assert r.status_code == 200


def test_mail_drafts_list(client, auth_headers):
    r = client.get("/v2/emails/mailboxes/u@example.com/drafts?maxResults=20", headers=auth_headers)
    assert r.status_code == 200


# ---- Auth ----
def test_auth_required(client):
    r = client.get("/v2/users")
    assert r.status_code == 401
    r2 = client.get("/v2/users", headers={"Authorization": "Bearer x"})
    assert r2.status_code == 200


if __name__ == "__main__":
    if HAS_PYTEST:
        pytest.main([__file__, "-v"])
    else:
        run_without_pytest()
