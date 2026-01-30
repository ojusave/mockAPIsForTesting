"""
Zoom-style data store. The source of truth for all data is the data/ directory only.
- data/accounts.json       → account list
- data/users/<id>.json     → full user profile + meeting_ids, recording refs
- data/meetings/<id>.json → meeting details + summary + vtt_data + recording_files + participants
- data/webinars/<id>.json → webinar details + participants
- data/tracking_fields.json, data/rooms.json, data/chat_*.json, data/qss_feedback.json

All reads and writes go to data/; no in-memory source of truth.
"""
import os
import json
from config import (
    BASE_URL, DATA_DIR, DATA_ACCOUNTS, DATA_USERS_DIR, DATA_MEETINGS_DIR, DATA_WEBINARS_DIR,
    DATA_TRACKING_FIELDS, DATA_ROOMS, DATA_CHAT_CHANNELS, DATA_CHAT_MESSAGES, DATA_QSS_FEEDBACK,
)

_accounts_cache = None
_user_ids_cache = None


def _load_json(path, default=None):
    if default is None:
        default = {}
    if not os.path.isfile(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def _list_json_files(dir_path):
    if not os.path.isdir(dir_path):
        return []
    return [
        os.path.splitext(f)[0]
        for f in os.listdir(dir_path)
        if f.endswith(".json")
    ]


# ---- Accounts (Zoom account structure) ----
def load_accounts():
    """Load accounts list from data/accounts.json."""
    global _accounts_cache
    if _accounts_cache is not None:
        return _accounts_cache
    data = _load_json(DATA_ACCOUNTS, default={"accounts": []})
    if isinstance(data, dict) and "accounts" in data:
        _accounts_cache = data["accounts"]
    else:
        _accounts_cache = data if isinstance(data, list) else []
    return _accounts_cache


def get_account(account_id):
    """Get a single account by id."""
    for acc in load_accounts():
        if acc.get("id") == account_id:
            return acc
    return None


# ---- Users (source of truth: data/users/) ----
def list_user_ids():
    """List all user ids from data/users/."""
    global _user_ids_cache
    if _user_ids_cache is not None:
        return _user_ids_cache
    _user_ids_cache = sorted(_list_json_files(DATA_USERS_DIR))
    return _user_ids_cache


def load_user(user_id):
    """Load user from data/users/<user_id>.json. Returns None if not found."""
    path = os.path.join(DATA_USERS_DIR, f"{user_id}.json")
    if not os.path.isfile(path):
        return None
    data = _load_json(path)
    return data if data else None


def save_user(user_id, payload):
    """Persist user to data/users/<id>.json (source of truth)."""
    payload = dict(payload)
    payload["id"] = user_id
    os.makedirs(DATA_USERS_DIR, exist_ok=True)
    path = os.path.join(DATA_USERS_DIR, f"{user_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    global _user_ids_cache
    _user_ids_cache = None


def add_meeting_to_user(user_id, meeting_id):
    """Add a meeting_id to user's meeting_ids and recording_meeting_ids. User must exist in data/users/."""
    u = load_user(user_id)
    if not u:
        return
    u = dict(u)
    mids = list(u.get("meeting_ids") or [])
    if meeting_id not in mids:
        mids.append(meeting_id)
    u["meeting_ids"] = mids
    recs = list(u.get("recording_meeting_ids") or [])
    if meeting_id not in recs:
        recs.append(meeting_id)
    u["recording_meeting_ids"] = recs
    save_user(user_id, u)


# ---- Meetings (source of truth: data/meetings/) ----
def list_meeting_ids():
    """List all meeting ids from data/meetings/."""
    return sorted(_list_json_files(DATA_MEETINGS_DIR))


def load_meeting(meeting_id):
    """Load meeting from data/meetings/<meeting_id>.json. Returns None if not found."""
    path = os.path.join(DATA_MEETINGS_DIR, f"{meeting_id}.json")
    if not os.path.isfile(path):
        return None
    data = _load_json(path)
    return data if data else None


def save_meeting(meeting_id, payload):
    """Persist meeting to data/meetings/<id>.json (source of truth)."""
    payload = dict(payload)
    payload["id"] = meeting_id
    payload["uuid"] = payload.get("uuid") or meeting_id
    os.makedirs(DATA_MEETINGS_DIR, exist_ok=True)
    path = os.path.join(DATA_MEETINGS_DIR, f"{meeting_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def get_meeting_summary_payload(meeting_id):
    """Get the meeting summary + vtt for a meeting. Returns None if not found."""
    m = load_meeting(meeting_id)
    if not m:
        return None
    summary = m.get("summary") or {}
    return {
        "meeting_id": m.get("id") or meeting_id,
        "meeting_uuid": m.get("uuid") or meeting_id,
        "meeting_topic": m.get("topic", ""),
        "summary_title": summary.get("summary_title", ""),
        "summary_overview": summary.get("summary_overview", ""),
        "summary_details": summary.get("summary_details", []),
        "next_steps": summary.get("next_steps", []),
        "vtt_data": m.get("vtt_data", ""),
    }


def get_vtt_for_meeting(meeting_id):
    """Return VTT transcript string for meeting, or None."""
    m = load_meeting(meeting_id)
    if not m:
        return None
    vtt = m.get("vtt_data", "")
    if isinstance(vtt, str) and vtt.strip():
        if not vtt.strip().upper().startswith("WEBVTT"):
            vtt = "WEBVTT\n\n" + vtt
        return vtt
    return None


def get_recordings_for_meeting(meeting_id):
    """Return recording_files array for a meeting from data store."""
    m = load_meeting(meeting_id)
    if not m:
        return []
    return m.get("recording_files") or []


def get_recordings_for_user(user_id, from_date=None, to_date=None):
    """
    Return list of recording objects (each with meeting info + recording_files) for user.
    Uses user's recording_meeting_ids or meeting_ids from user file, then loads each meeting.
    Optionally filter by from_date / to_date (string YYYY-MM-DD) based on meeting start_time.
    """
    u = load_user(user_id)
    if not u:
        return []
    meeting_ids = u.get("recording_meeting_ids") or u.get("meeting_ids") or []
    out = []
    for mid in meeting_ids:
        m = load_meeting(mid)
        if not m:
            continue
        files = m.get("recording_files") or []
        if not files:
            continue
        start_str = (m.get("start_time") or "")[:10]
        if from_date and start_str < from_date:
            continue
        if to_date and start_str > to_date:
            continue
        out.append({
            "uuid": m.get("uuid") or mid,
            "id": m.get("id") or mid,
            "host_id": m.get("host_id") or user_id,
            "topic": m.get("topic", ""),
            "start_time": m.get("start_time", ""),
            "duration": m.get("duration", 60),
            "total_size": sum(f.get("file_size", 0) for f in files),
            "recording_count": len(files),
            "recording_files": files,
        })
    return out


def get_participants_for_meeting(meeting_id):
    """Return participants array for past meeting from data store."""
    m = load_meeting(meeting_id)
    if not m:
        return []
    return m.get("participants") or []


def get_meetings_for_user(user_id, from_date=None, to_date=None):
    """
    Return list of meeting objects for user from data store (from user's meeting_ids).
    Optionally filter by from_date / to_date (string YYYY-MM-DD).
    """
    u = load_user(user_id)
    if not u:
        return []
    meeting_ids = u.get("meeting_ids") or []
    meetings = []
    for mid in meeting_ids:
        m = load_meeting(mid)
        if not m:
            continue
        # Return Zoom list-meeting shape (uuid, id, host_id, topic, type, start_time, duration, timezone, created_at, join_url)
        start = m.get("start_time") or ""
        if from_date and start < from_date:
            continue
        if to_date and start > to_date + "T23:59:59":
            continue
        meetings.append({
            "uuid": m.get("uuid") or mid,
            "id": m.get("id") or mid,
            "host_id": m.get("host_id") or user_id,
            "topic": m.get("topic", ""),
            "type": m.get("type", 2),
            "start_time": m.get("start_time", ""),
            "duration": m.get("duration", 60),
            "timezone": m.get("timezone", "America/New_York"),
            "created_at": m.get("created_at", ""),
            "join_url": m.get("join_url") or f"{BASE_URL}/j/{mid}",
        })
    return meetings


# ---- Webinars (Zoom webinar: type 5, separate from meetings) ----
def list_webinar_ids():
    """List all webinar ids (from filenames in data/webinars/)."""
    return _list_json_files(DATA_WEBINARS_DIR)


def load_webinar(webinar_id):
    """Load webinar from data/webinars/<webinar_id>.json. Returns None if not found."""
    path = os.path.join(DATA_WEBINARS_DIR, f"{webinar_id}.json")
    if not os.path.isfile(path):
        return None
    data = _load_json(path)
    return data if data else None


def get_webinars_for_user(user_id, from_date=None, to_date=None):
    """Return list of webinar objects for user (from user's webinar_ids). Filter by from_date/to_date (YYYY-MM-DD)."""
    u = load_user(user_id)
    if not u:
        return []
    webinar_ids = u.get("webinar_ids") or []
    webinars = []
    for wid in webinar_ids:
        w = load_webinar(wid)
        if not w:
            continue
        start = (w.get("start_time") or "")[:10]
        if from_date and start < from_date:
            continue
        if to_date and start > to_date:
            continue
        webinars.append({
            "uuid": w.get("uuid") or wid,
            "id": w.get("id") or wid,
            "host_id": w.get("host_id") or user_id,
            "topic": w.get("topic", ""),
            "type": 5,
            "start_time": w.get("start_time", ""),
            "duration": w.get("duration", 60),
            "timezone": w.get("timezone", "America/New_York"),
            "created_at": w.get("created_at", ""),
            "join_url": w.get("join_url") or f"{BASE_URL}/w/{wid}",
        })
    return webinars


def get_participants_for_webinar(webinar_id):
    """Return participants array for past webinar from data store."""
    w = load_webinar(webinar_id)
    if not w:
        return []
    return w.get("participants") or []


# ---- Tracking fields (source of truth: data/tracking_fields.json) ----
def load_tracking_fields():
    """Load tracking fields list from data/tracking_fields.json."""
    data = _load_json(DATA_TRACKING_FIELDS, default={"tracking_fields": []})
    if isinstance(data, dict) and "tracking_fields" in data:
        return data["tracking_fields"]
    return data if isinstance(data, list) else []


def save_tracking_fields(fields):
    """Persist tracking fields to data/tracking_fields.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_TRACKING_FIELDS, "w", encoding="utf-8") as f:
        json.dump({"tracking_fields": fields}, f, indent=2)


# ---- Rooms (source of truth: data/rooms.json) ----
def load_rooms():
    """Load rooms list from data/rooms.json."""
    data = _load_json(DATA_ROOMS, default={"rooms": []})
    if isinstance(data, dict) and "rooms" in data:
        return data["rooms"]
    return data if isinstance(data, list) else []


def save_rooms(rooms):
    """Persist rooms to data/rooms.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_ROOMS, "w", encoding="utf-8") as f:
        json.dump({"rooms": rooms}, f, indent=2)


# ---- Chat (source of truth: data/chat_channels.json, data/chat_messages.json) ----
def load_chat_channels():
    """Load chat channels from data/chat_channels.json. Returns dict id -> channel."""
    data = _load_json(DATA_CHAT_CHANNELS, default={"channels": {}})
    if isinstance(data, dict) and "channels" in data:
        return data["channels"]
    return data if isinstance(data, dict) else {}


def save_chat_channels(channels):
    """Persist chat channels to data/chat_channels.json. channels: dict id -> channel."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_CHAT_CHANNELS, "w", encoding="utf-8") as f:
        json.dump({"channels": channels}, f, indent=2)


def load_chat_messages():
    """Load all chat messages from data/chat_messages.json. Returns dict channel_id -> list of messages."""
    data = _load_json(DATA_CHAT_MESSAGES, default={"messages": {}})
    if isinstance(data, dict) and "messages" in data:
        return data["messages"]
    return data if isinstance(data, dict) else {}


def save_chat_messages(messages):
    """Persist chat messages to data/chat_messages.json. messages: dict channel_id -> list."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_CHAT_MESSAGES, "w", encoding="utf-8") as f:
        json.dump({"messages": messages}, f, indent=2)


# ---- QSS feedback (source of truth: data/qss_feedback.json) ----
def load_qss_feedback():
    """Load QSS feedback from data/qss_feedback.json. Returns dict id -> feedback."""
    data = _load_json(DATA_QSS_FEEDBACK, default={"feedback": {}})
    if isinstance(data, dict) and "feedback" in data:
        return data["feedback"]
    return data if isinstance(data, dict) else {}


def save_qss_feedback(feedback):
    """Persist QSS feedback to data/qss_feedback.json. feedback: dict id -> entry."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_QSS_FEEDBACK, "w", encoding="utf-8") as f:
        json.dump({"feedback": feedback}, f, indent=2)
