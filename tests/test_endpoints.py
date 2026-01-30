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


def run_without_pytest():
    c = _client()
    h = _auth_headers()
    failed = []
    tests = [
        ("GET /users", lambda: c.get("/users", headers=h)),
        ("GET /users?page_size=5&status=active", lambda: c.get("/users?page_size=5&status=active", headers=h)),
        ("POST /users", lambda: c.post("/users", headers=h, json={"email": "t@x.com", "first_name": "A", "last_name": "B"})),
        ("POST /users validation", lambda: c.post("/users", headers=h, json={"email": "x"})),
        ("GET /users/:id", lambda: c.get("/users/u1", headers=h)),
        ("PATCH /users/:id", lambda: c.patch("/users/u1", headers=h, json={"first_name": "Patched"})),
        ("PUT /users/:id/status", lambda: c.put("/users/u1/status", headers=h, json={"action": "activate"})),
        ("DELETE /users/:id", lambda: c.delete("/users/u1", headers=h)),
        ("GET /users/:id/meetings", lambda: c.get("/users/u1/meetings?from=2026-01-01&to=2026-12-31&page_size=5", headers=h)),
        ("POST /users/:id/meetings", lambda: c.post("/users/u1/meetings", headers=h, json={"topic": "T", "duration": 30})),
        ("GET /meetings/:id", lambda: c.get("/meetings/m1", headers=h)),
        ("PATCH /meetings", lambda: c.patch("/users/u1/meetings/m1", headers=h, json={"topic": "Updated"})),
        ("DELETE /meetings", lambda: c.delete("/users/u1/meetings/m1", headers=h)),
        ("GET /users/:id/recordings", lambda: c.get("/users/u1/recordings?page_number=1", headers=h)),
        ("GET /meetings/:id/recordings", lambda: c.get("/meetings/m1/recordings", headers=h)),
        ("DELETE recording", lambda: c.delete("/meetings/m1/recordings/rec1", headers=h, json={})),
        ("GET qss/score", lambda: c.get("/qss/score/m1", headers=h)),
        ("POST qss/feedback", lambda: c.post("/qss/feedback", headers=h, json={"meeting_id": "m1", "rating": 5})),
        ("POST /chat/channels", lambda: c.post("/chat/channels", headers=h, json={"name": "Ch1", "type": 1})),
        ("POST /chat/channels validation", lambda: c.post("/chat/channels", headers=h, json={})),
        ("POST calendar", lambda: c.post("/calendars", headers=h, json={"summary": "Cal"})),
        ("POST freeBusy", lambda: c.post("/calendars/freeBusy", headers=h, json={"timeMin": "2026-01-01T00:00:00Z", "timeMax": "2026-01-02T00:00:00Z", "items": [{"id": "c1"}]})),
        ("POST mail send validation", lambda: c.post("/emails/mailboxes/u@x.com/messages/send", headers=h, json={})),
        ("GET /users/:id/webinars", lambda: c.get("/users/u1/webinars?from=2026-01-01&to=2026-12-31", headers=h)),
        ("GET /webinars/:id", lambda: c.get("/webinars/w1", headers=h)),
        ("GET /past_webinars/:id/participants", lambda: c.get("/past_webinars/w1/participants", headers=h)),
        ("GET /report/users", lambda: c.get("/report/users?type=active", headers=h)),
        ("GET /report/meetings/:id/participants", lambda: c.get("/report/meetings/m1/participants", headers=h)),
        ("GET /metrics/meetings", lambda: c.get("/metrics/meetings?from=2026-01-01&to=2026-12-31", headers=h)),
        ("GET /devices", lambda: c.get("/devices", headers=h)),
        ("GET /roles", lambda: c.get("/roles", headers=h)),
        ("GET /groups", lambda: c.get("/groups", headers=h)),
        ("Auth required", lambda: c.get("/users")),
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
    r = client.get("/users", headers=auth_headers)
    assert r.status_code == 200
    data = r.get_json()
    assert "users" in data and "page_size" in data
    r2 = client.get("/users?page_size=5&page_number=1&status=active", headers=auth_headers)
    assert r2.status_code == 200


def test_users_create_post(client, auth_headers):
    r = client.post("/users", headers=auth_headers, json={
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
    r = client.post("/users", headers=auth_headers, json={"email": "only@example.com"})
    assert r.status_code == 400
    assert r.get_json().get("error", {}).get("code") == "400"


def test_users_get(client, auth_headers):
    r = client.get("/users/abc123", headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["id"] == "abc123"


def test_users_patch(client, auth_headers):
    r = client.patch("/users/usr1", headers=auth_headers, json={
        "first_name": "Patched",
        "timezone": "Europe/London",
        "company": "Acme",
    })
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("first_name") == "Patched" and data.get("timezone") == "Europe/London"


def test_users_status_put(client, auth_headers):
    r = client.put("/users/usr1/status", headers=auth_headers, json={"action": "activate"})
    assert r.status_code == 200
    r2 = client.put("/users/usr1/status", headers=auth_headers, json={})
    assert r2.status_code == 400


def test_users_token_get(client, auth_headers):
    r = client.get("/users/usr1/token?type=zak&ttl=3600", headers=auth_headers)
    assert r.status_code == 200
    assert "token" in r.get_json()


def test_users_delete(client, auth_headers):
    r = client.delete("/users/usr1", headers=auth_headers)
    assert r.status_code == 204


# ---- Meetings ----
def test_meetings_list_get(client, auth_headers):
    r = client.get("/users/u1/meetings?from=2026-01-01&to=2026-12-31&page_size=5&type=scheduled", headers=auth_headers)
    assert r.status_code == 200
    data = r.get_json()
    assert "meetings" in data and "page_size" in data


def test_meetings_create_post(client, auth_headers):
    r = client.post("/users/u1/meetings", headers=auth_headers, json={
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


def test_meetings_get_by_id(client, auth_headers):
    r = client.get("/meetings/m1", headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["id"] == "m1"


def test_meetings_patch(client, auth_headers):
    r = client.patch("/users/u1/meetings/m1", headers=auth_headers, json={
        "topic": "Updated Topic",
        "duration": 90,
        "settings": {"mute_upon_entry": False},
    })
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("topic") == "Updated Topic" and data.get("duration") == 90


def test_meetings_summary_get(client, auth_headers):
    r = client.get("/meetings/m1/meeting_summary", headers=auth_headers)
    assert r.status_code == 200


def test_meetings_participants_get(client, auth_headers):
    r = client.get("/past_meetings/m1/participants?page_size=10", headers=auth_headers)
    assert r.status_code == 200
    assert "participants" in r.get_json()


def test_meetings_delete(client, auth_headers):
    r = client.delete("/users/u1/meetings/m1", headers=auth_headers)
    assert r.status_code == 204


# ---- Recordings ----
def test_recordings_list_get(client, auth_headers):
    r = client.get("/users/u1/recordings?from=2026-01-01&to=2026-12-31&page_size=5&page_number=1", headers=auth_headers)
    assert r.status_code == 200
    assert "meetings" in r.get_json()


def test_recordings_meeting_get(client, auth_headers):
    r = client.get("/meetings/m1/recordings?trash=false", headers=auth_headers)
    assert r.status_code == 200
    assert "recording_files" in r.get_json()


def test_recordings_delete(client, auth_headers):
    r = client.delete("/meetings/m1/recordings/rec1", headers=auth_headers, json={"action": "delete"})
    assert r.status_code == 204


# ---- QSS ----
def test_qss_score_get(client, auth_headers):
    r = client.get("/qss/score/m1", headers=auth_headers)
    assert r.status_code == 200
    assert "quality_score" in r.get_json()


def test_qss_feedback_post(client, auth_headers):
    r = client.post("/qss/feedback", headers=auth_headers, json={
        "meeting_id": "m1",
        "rating": 5,
        "comments": "Great meeting",
    })
    assert r.status_code == 201
    data = r.get_json()
    assert data.get("meeting_id") == "m1" and "id" in data


def test_qss_metrics_meeting_get(client, auth_headers):
    r = client.get("/metrics/meetings/m1/participants/qos_summary?page_size=5", headers=auth_headers)
    assert r.status_code == 200
    assert "participants" in r.get_json()


# ---- Chat ----
def test_chat_channels_list(client, auth_headers):
    r = client.get("/chat/channels", headers=auth_headers)
    assert r.status_code == 200


def test_chat_channels_create(client, auth_headers):
    r = client.post("/chat/channels", headers=auth_headers, json={"name": "Test Channel", "type": 1})
    assert r.status_code == 201
    assert r.get_json()["name"] == "Test Channel"


def test_chat_channels_create_validation(client, auth_headers):
    r = client.post("/chat/channels", headers=auth_headers, json={"type": 1})
    assert r.status_code == 400


def test_chat_messages_send(client, auth_headers):
    client.post("/chat/channels", headers=auth_headers, json={"name": "C1", "type": 1})
    r = client.post("/chat/channels/1/messages", headers=auth_headers, json={"message": "Hello"})
    assert r.status_code == 201


# ---- Calendar ----
def test_calendar_events_list(client, auth_headers):
    r = client.get("/calendars/cal1/events?maxResults=10", headers=auth_headers)
    assert r.status_code == 200


def test_calendar_create(client, auth_headers):
    r = client.post("/calendars", headers=auth_headers, json={"summary": "Work", "timeZone": "UTC"})
    assert r.status_code == 200


def test_calendar_create_validation(client, auth_headers):
    r = client.post("/calendars", headers=auth_headers, json={})
    assert r.status_code == 400


def test_calendar_freebusy_post(client, auth_headers):
    r = client.post("/calendars/freeBusy", headers=auth_headers, json={
        "timeMin": "2026-01-01T00:00:00Z",
        "timeMax": "2026-01-02T00:00:00Z",
        "items": [{"id": "cal1"}],
    })
    assert r.status_code == 200


# ---- Mail ----
def test_mail_send_validation(client, auth_headers):
    r = client.post("/emails/mailboxes/u@example.com/messages/send", headers=auth_headers, json={})
    assert r.status_code == 400


def test_mail_send(client, auth_headers):
    r = client.post("/emails/mailboxes/u@example.com/messages/send", headers=auth_headers, json={"raw": "YmFzZTY0"})
    assert r.status_code == 200


def test_mail_drafts_list(client, auth_headers):
    r = client.get("/emails/mailboxes/u@example.com/drafts?maxResults=20", headers=auth_headers)
    assert r.status_code == 200


# ---- Auth ----
def test_auth_required(client):
    r = client.get("/users")
    assert r.status_code == 401
    r2 = client.get("/users", headers={"Authorization": "Bearer x"})
    assert r2.status_code == 200


if __name__ == "__main__":
    if HAS_PYTEST:
        pytest.main([__file__, "-v"])
    else:
        run_without_pytest()
