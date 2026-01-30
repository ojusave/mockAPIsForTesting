"""
Zoom-style data store. All API data is read from the data/ directory:
- data/accounts.json     → account list (Zoom account structure)
- data/users/<id>.json   → full user profile + meeting_ids, recording refs
- data/meetings/<id>.json → meeting details + summary + vtt_data + recording_files + participants
- data/webinars/<id>.json → webinar details + participants

API routes use this module to serve GET/POST/PATCH/DELETE from file-backed data.
"""
import os
import json
from config import BASE_URL, DATA_DIR, DATA_ACCOUNTS, DATA_USERS_DIR, DATA_MEETINGS_DIR, DATA_WEBINARS_DIR

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


# ---- Users (full Zoom user profile per file) ----
def list_user_ids():
    """List all user ids (from filenames in data/users/)."""
    global _user_ids_cache
    if _user_ids_cache is not None:
        return _user_ids_cache
    _user_ids_cache = _list_json_files(DATA_USERS_DIR)
    return _user_ids_cache


def load_user(user_id):
    """
    Load full user profile from data/users/<user_id>.json.
    File shape: Zoom user object (id, first_name, last_name, email, type, pmi, timezone, ...)
    plus optional: meeting_ids[], recording_meeting_ids[] (meetings that have recordings).
    """
    path = os.path.join(DATA_USERS_DIR, f"{user_id}.json")
    return _load_json(path)


def save_user(user_id, payload):
    """Overwrite user file (for PATCH/create). Used only if you want mock to persist."""
    os.makedirs(DATA_USERS_DIR, exist_ok=True)
    path = os.path.join(DATA_USERS_DIR, f"{user_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    global _user_ids_cache
    _user_ids_cache = None


# ---- Meetings (Zoom meeting + summary + vtt + recording_files + participants) ----
def list_meeting_ids():
    """List all meeting ids (from filenames in data/meetings/)."""
    return _list_json_files(DATA_MEETINGS_DIR)


def load_meeting(meeting_id):
    """
    Load meeting from data/meetings/<meeting_id>.json.
    Expected keys: Zoom meeting (uuid, id, host_id, topic, type, start_time, duration, ...),
    summary {}, vtt_data "", recording_files [], participants [].
    """
    path = os.path.join(DATA_MEETINGS_DIR, f"{meeting_id}.json")
    return _load_json(path)


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
    """Load webinar from data/webinars/<webinar_id>.json."""
    path = os.path.join(DATA_WEBINARS_DIR, f"{webinar_id}.json")
    return _load_json(path)


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
