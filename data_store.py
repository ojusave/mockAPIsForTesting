"""
Zoom-style data store. API data is read from the data/ directory and/or in-memory store.
- data/users/<id>.json   → full user profile + meeting_ids, recording refs
- data/meetings/<id>.json → meeting details + summary + vtt_data + recording_files + participants
- data/webinars/<id>.json → webinar details + participants

Any ID requested that is not in file or memory gets a generated mock entity (stored in memory)
so that "whatever they input returns a result" for mock testing.
Creates (POST) persist to memory and optionally to file.
"""
import os
import json
import datetime
from config import BASE_URL, DATA_DIR, DATA_ACCOUNTS, DATA_USERS_DIR, DATA_MEETINGS_DIR, DATA_WEBINARS_DIR

_accounts_cache = None
_user_ids_cache = None

# In-memory store for created/generated entities (any input returns a result)
_memory_users = {}
_memory_meetings = {}
_memory_webinars = {}


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


def _build_mock_meeting(meeting_id, host_id="mock_host"):
    """Build a full mock meeting (summary, vtt_data, recording_files, participants) for any ID."""
    now = datetime.datetime.utcnow()
    start = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    rec_id = f"rec_{meeting_id}"
    return {
        "uuid": meeting_id,
        "id": meeting_id,
        "host_id": host_id,
        "host_email": f"{host_id}@zoom-mock.com",
        "topic": f"Meeting {meeting_id}",
        "type": 2,
        "start_time": start,
        "duration": 60,
        "timezone": "America/New_York",
        "created_at": start,
        "join_url": f"{BASE_URL}/j/{meeting_id}",
        "start_url": f"{BASE_URL}/s/{meeting_id}",
        "password": "mock123",
        "agenda": "",
        "settings": {"host_video": True, "participant_video": False, "mute_upon_entry": True, "waiting_room": True},
        "summary": {
            "summary_title": f"Meeting {meeting_id}",
            "summary_overview": "Mock summary for testing.",
            "summary_details": ["Point 1", "Point 2"],
            "next_steps": ["Follow up"],
        },
        "vtt_data": f"WEBVTT\n\n00:00:00 --> 00:01:00 Speaker: Mock transcript for {meeting_id}.",
        "recording_files": [
            {
                "id": rec_id,
                "meeting_id": meeting_id,
                "recording_start": start,
                "recording_end": start,
                "file_type": "MP4",
                "file_extension": "MP4",
                "file_size": 1000000,
                "play_url": f"{BASE_URL}/rec/play/{rec_id}",
                "download_url": f"{BASE_URL}/rec/download/{meeting_id}/transcript.vtt",
                "status": "completed",
            }
        ],
        "participants": [
            {"id": f"p_{meeting_id}", "name": "Participant", "user_id": host_id, "user_email": f"{host_id}@zoom-mock.com", "join_time": start, "leave_time": start, "duration": 3600}
        ],
    }


def get_or_create_mock_user(user_id):
    """Return a mock user for any ID; store in memory so subsequent GETs are consistent."""
    from helpers import generate_base_user_data
    data = generate_base_user_data()
    data["id"] = user_id
    data["email"] = data.get("email") or f"{user_id}@zoom-mock.com"
    data["meeting_ids"] = [f"{user_id}_m1"]
    data["recording_meeting_ids"] = [f"{user_id}_m1"]
    data["webinar_ids"] = [f"{user_id}_w1"]
    _memory_users[user_id] = data
    global _user_ids_cache
    _user_ids_cache = None
    return data


def get_or_create_mock_meeting(meeting_id, host_id=None):
    """Return a mock meeting for any ID; store in memory. Infers host from id when e.g. user_id_m1."""
    if host_id is None and meeting_id.endswith("_m1"):
        host_id = meeting_id[:-3]
    m = _build_mock_meeting(meeting_id, host_id=host_id or "mock_host")
    _memory_meetings[meeting_id] = m
    return m


def get_or_create_mock_webinar(webinar_id, host_id=None):
    """Return a mock webinar for any ID; store in memory."""
    host_id = host_id or "mock_host"
    now = datetime.datetime.utcnow()
    start = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    w = {
        "uuid": webinar_id,
        "id": webinar_id,
        "host_id": host_id,
        "topic": f"Webinar {webinar_id}",
        "type": 5,
        "start_time": start,
        "duration": 60,
        "timezone": "America/New_York",
        "created_at": start,
        "join_url": f"{BASE_URL}/w/{webinar_id}",
        "participants": [{"id": f"wp_{webinar_id}", "name": "Attendee", "user_id": host_id}],
    }
    _memory_webinars[webinar_id] = w
    return w


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


# ---- Users (full Zoom user profile per file + in-memory) ----
def list_user_ids():
    """List all user ids (from data/users/ files + in-memory store)."""
    global _user_ids_cache
    if _user_ids_cache is not None:
        return _user_ids_cache
    file_ids = _list_json_files(DATA_USERS_DIR)
    _user_ids_cache = sorted(set(file_ids) | set(_memory_users.keys()))
    return _user_ids_cache


def load_user(user_id):
    """
    Load user: in-memory first, then data/users/<user_id>.json.
    If not found, create and store a mock user for that ID (any input returns a result).
    """
    if user_id in _memory_users:
        return dict(_memory_users[user_id])
    path = os.path.join(DATA_USERS_DIR, f"{user_id}.json")
    if os.path.isfile(path):
        data = _load_json(path)
        if data:
            return data
    return get_or_create_mock_user(user_id)


def save_user(user_id, payload):
    """Persist user to in-memory store and optionally to file (data/users/<id>.json)."""
    payload = dict(payload)
    payload["id"] = user_id
    _memory_users[user_id] = payload
    os.makedirs(DATA_USERS_DIR, exist_ok=True)
    path = os.path.join(DATA_USERS_DIR, f"{user_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    global _user_ids_cache
    _user_ids_cache = None


def add_meeting_to_user(user_id, meeting_id):
    """Add a meeting_id to user's meeting_ids and recording_meeting_ids (used after creating a meeting)."""
    u = load_user(user_id)
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


# ---- Meetings (Zoom meeting + summary + vtt + recording_files + participants) ----
def list_meeting_ids():
    """List all meeting ids (from data/meetings/ files + in-memory store)."""
    return sorted(set(_list_json_files(DATA_MEETINGS_DIR)) | set(_memory_meetings.keys()))


def load_meeting(meeting_id):
    """
    Load meeting: in-memory first, then data/meetings/<meeting_id>.json.
    If not found, create and store a mock meeting for that ID (any input returns a result).
    """
    if meeting_id in _memory_meetings:
        return dict(_memory_meetings[meeting_id])
    path = os.path.join(DATA_MEETINGS_DIR, f"{meeting_id}.json")
    if os.path.isfile(path):
        data = _load_json(path)
        if data:
            return data
    return get_or_create_mock_meeting(meeting_id)


def save_meeting(meeting_id, payload):
    """Persist meeting to in-memory store and optionally to file (data/meetings/<id>.json)."""
    payload = dict(payload)
    payload["id"] = meeting_id
    payload["uuid"] = payload.get("uuid") or meeting_id
    _memory_meetings[meeting_id] = payload
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
    """
    Load webinar: in-memory first, then data/webinars/<webinar_id>.json.
    If not found, create and store a mock webinar for that ID (any input returns a result).
    """
    if webinar_id in _memory_webinars:
        return dict(_memory_webinars[webinar_id])
    path = os.path.join(DATA_WEBINARS_DIR, f"{webinar_id}.json")
    if os.path.isfile(path):
        data = _load_json(path)
        if data:
            return data
    return get_or_create_mock_webinar(webinar_id)


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
