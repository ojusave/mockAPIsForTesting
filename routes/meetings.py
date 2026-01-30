from flask import Blueprint, jsonify, request
from helpers import generate_random_string, BASE_URL
from config import DEFAULT_DATE_FROM, DEFAULT_DATE_TO, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from cache_config import cache
from models.auth import require_auth
from data_store import (
    load_meeting,
    get_meetings_for_user,
    get_meeting_summary_payload,
    get_participants_for_meeting,
    save_meeting,
    add_meeting_to_user,
)
import datetime

meetings_bp = Blueprint("meetings", __name__)


@meetings_bp.route("/users/<user_id>/meetings", methods=["POST"])
@require_auth
def create_meeting(user_id):
    """Create a meeting. Body: topic, type, start_time, duration, timezone, agenda, schedule_for, settings, template_id, password."""
    data = request.get_json() or {}
    topic = data.get("topic", "My Meeting")
    meeting_id = generate_random_string(22)
    start_str = data.get("start_time")
    if start_str:
        try:
            if "T" in start_str:
                start = datetime.datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            else:
                start = datetime.datetime.strptime(start_str[:10], "%Y-%m-%d") + datetime.timedelta(hours=12)
        except (ValueError, TypeError):
            start = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    else:
        start = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    duration = int(data.get("duration", 60))
    default_settings = {
        "host_video": True,
        "participant_video": False,
        "join_before_host": False,
        "mute_upon_entry": True,
        "waiting_room": True,
    }
    settings = dict(default_settings, **(data.get("settings") or {}))
    payload = {
        "uuid": meeting_id,
        "id": meeting_id,
        "host_id": user_id,
        "topic": topic,
        "type": int(data.get("type", 2)),
        "start_time": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration": duration,
        "timezone": data.get("timezone", "America/New_York"),
        "agenda": data.get("agenda", ""),
        "created_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "join_url": f"{BASE_URL}/j/{meeting_id}",
        "start_url": f"{BASE_URL}/s/{meeting_id}",
        "password": data.get("password") or generate_random_string(6),
        "settings": settings,
    }
    if data.get("schedule_for"):
        payload["schedule_for"] = data["schedule_for"]
    if data.get("template_id"):
        payload["template_id"] = data["template_id"]
    save_meeting(meeting_id, payload)
    add_meeting_to_user(user_id, meeting_id)
    return jsonify(payload), 201


@meetings_bp.route("/users/<user_id>/meetings", methods=["GET"])
@require_auth
def get_meetings(user_id):
    """List meetings from data store for user. Query: from, to (YYYY-MM-DD), page_size, page_number, type."""
    from_date = request.args.get("from", DEFAULT_DATE_FROM)
    to_date = request.args.get("to", DEFAULT_DATE_TO)
    page_size = min(int(request.args.get("page_size", DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)
    page_number = max(1, int(request.args.get("page_number", 1)))
    meeting_type = request.args.get("type")
    try:
        datetime.datetime.strptime(from_date, "%Y-%m-%d")
        datetime.datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": {"code": "400", "message": "Invalid date format", "details": "Use YYYY-MM-DD for from and to"}}), 400
    meetings = get_meetings_for_user(user_id, from_date=from_date, to_date=to_date)
    if meeting_type and meeting_type in ("scheduled", "live", "upcoming"):
        meetings = [m for m in meetings if m.get("type") == 2]
    total = len(meetings)
    start = (page_number - 1) * page_size
    page_meetings = meetings[start : start + page_size]
    response_data = {
        "page_size": page_size,
        "page_number": page_number,
        "total_records": total,
        "next_page_token": generate_random_string(16) if start + page_size < total else "",
        "meetings": page_meetings,
    }
    return jsonify(response_data)


def _meeting_to_zoom_response(m):
    """Return Zoom GET meeting shape (exclude summary, vtt_data, participants)."""
    if not m:
        return None
    return {
        k: v for k, v in m.items()
        if k not in ("summary", "vtt_data", "participants", "recording_files")
    }


@meetings_bp.route("/meetings/<meeting_id>", methods=["GET"])
@require_auth
@cache.memoize(timeout=3600)
def get_meeting_by_id(meeting_id):
    """Get meeting by ID from data/meetings/<meeting_id>.json (Zoom-style). 404 if not found."""
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found", "details": f"No meeting with id: {meeting_id}"}}), 404
    return jsonify(_meeting_to_zoom_response(m))


@meetings_bp.route("/users/<user_id>/meetings/<meeting_id>", methods=["GET"])
@require_auth
@cache.memoize(timeout=3600)
def get_meeting(user_id, meeting_id):
    """Get meeting from data store. 404 if not found."""
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found", "details": f"No meeting with id: {meeting_id}"}}), 404
    return jsonify(_meeting_to_zoom_response(m))


@meetings_bp.route("/meetings/<meeting_id>/meeting_summary", methods=["GET"])
@require_auth
@cache.memoize(timeout=3600)
def get_meeting_summary(meeting_id):
    """Get meeting summary from data/meetings/<meeting_id>.json. 404 if not found."""
    payload = get_meeting_summary_payload(meeting_id)
    if not payload:
        return jsonify({"error": {"code": "404", "message": "Meeting or summary not found", "details": f"No meeting with id: {meeting_id}"}}), 404
    m = load_meeting(meeting_id)
    start_time = (m or {}).get("start_time", "") or "2026-01-15T14:00:00Z"
    duration = (m or {}).get("duration", 60)
    meeting_summary = {
        "meeting_host_id": (m or {}).get("host_id", ""),
        "meeting_host_email": (m or {}).get("host_email", ""),
        "meeting_uuid": payload.get("meeting_uuid", meeting_id),
        "meeting_id": payload.get("meeting_id", meeting_id),
        "meeting_topic": payload.get("meeting_topic", ""),
        "meeting_start_time": start_time,
        "meeting_end_time": start_time,
        "summary_start_time": start_time,
        "summary_end_time": start_time,
        "summary_created_time": start_time,
        "summary_last_modified_time": start_time,
        "summary_title": payload.get("summary_title", ""),
        "summary_overview": payload.get("summary_overview", ""),
        "summary_details": [
            {"label": "Meeting overview", "summary": payload.get("summary_overview", "")}
        ] + [{"label": f"Point {i+1}", "summary": d} for i, d in enumerate(payload.get("summary_details") or [])],
        "next_steps": payload.get("next_steps", []),
        "edited_summary": {
            "summary_details": payload.get("summary_overview", ""),
            "next_steps": payload.get("next_steps", []),
        },
    }
    return jsonify(meeting_summary)


@meetings_bp.route("/past_meetings/<meeting_id>/participants", methods=["GET"])
@require_auth
def get_past_meeting_participants(meeting_id):
    """List past meeting participants from data/meetings/<meeting_id>.json. 404 if not found."""
    participants = get_participants_for_meeting(meeting_id)
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found", "details": f"No meeting with id: {meeting_id}"}}), 404
    page_size = min(int(request.args.get("page_size", 30)), 300)
    page_number = max(1, int(request.args.get("page_number", 1)))
    total = len(participants)
    start = (page_number - 1) * page_size
    page_participants = participants[start : start + page_size]
    response_data = {
        "next_page_token": generate_random_string(32) if start + page_size < total else "",
        "page_count": max(1, (total + page_size - 1) // page_size),
        "page_size": page_size,
        "total_records": total,
        "participants": page_participants,
    }
    return jsonify(response_data)


@meetings_bp.route("/users/<user_id>/meetings/<meeting_id>", methods=["PATCH"])
@require_auth
def update_meeting(user_id, meeting_id):
    """Update meeting. Body merged into data from data/meetings/<meeting_id>.json; 404 if not found."""
    data = request.get_json() or {}
    cache.delete_memoized(get_meeting, user_id, meeting_id)
    cache.delete_memoized(get_meeting_by_id, meeting_id)
    cache.delete_memoized(get_meeting_summary, meeting_id)
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found", "details": f"No meeting with id: {meeting_id}"}}), 404
    payload = dict(_meeting_to_zoom_response(m))
    for key in ("topic", "duration", "timezone", "agenda", "password"):
        if key in data:
            payload[key] = data[key]
    if "start_time" in data:
        payload["start_time"] = data["start_time"]
    if "settings" in data:
        payload["settings"] = dict(payload.get("settings", {}), **data["settings"])
    save_meeting(meeting_id, payload)
    return jsonify(payload), 200


@meetings_bp.route("/users/<user_id>/meetings/<meeting_id>", methods=["DELETE"])
@require_auth
def delete_meeting(user_id, meeting_id):
    cache.delete_memoized(get_meeting, user_id, meeting_id)
    cache.delete_memoized(get_meeting_by_id, meeting_id)
    cache.delete_memoized(get_meeting_summary, meeting_id)
    return "", 204


# ---- Meeting polls (Zoom API: developers.zoom.us/docs/api/) ----
@meetings_bp.route("/meetings/<meeting_id>/polls", methods=["GET"])
@require_auth
def list_meeting_polls(meeting_id):
    """List meeting polls. Returns 404 if meeting not found."""
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found"}}), 404
    return jsonify({"polls": m.get("polls", [])})


@meetings_bp.route("/meetings/<meeting_id>/polls", methods=["POST"])
@require_auth
def create_meeting_poll(meeting_id):
    """Create a meeting poll. Body: title, questions[].name, questions[].type."""
    data = request.get_json() or {}
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found"}}), 404
    poll_id = generate_random_string(16)
    poll = {"id": poll_id, "title": data.get("title", "Poll"), "questions": data.get("questions", [])}
    return jsonify(poll), 201


@meetings_bp.route("/meetings/<meeting_id>/polls/<poll_id>", methods=["GET"])
@require_auth
def get_meeting_poll(meeting_id, poll_id):
    """Get a meeting poll by ID."""
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found"}}), 404
    polls = m.get("polls", [])
    poll = next((p for p in polls if p.get("id") == poll_id), None)
    if not poll:
        return jsonify({"error": {"code": "404", "message": "Poll not found"}}), 404
    return jsonify(poll)


@meetings_bp.route("/meetings/<meeting_id>/polls/<poll_id>", methods=["PATCH"])
@require_auth
def update_meeting_poll(meeting_id, poll_id):
    """Update a meeting poll. Body: title, questions."""
    data = request.get_json() or {}
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found"}}), 404
    poll = {"id": poll_id, "title": data.get("title", "Poll"), "questions": data.get("questions", [])}
    return jsonify(poll), 200


@meetings_bp.route("/meetings/<meeting_id>/polls/<poll_id>", methods=["DELETE"])
@require_auth
def delete_meeting_poll(meeting_id, poll_id):
    """Delete a meeting poll."""
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found"}}), 404
    return "", 204


# ---- Meeting registrants (Zoom API) ----
@meetings_bp.route("/meetings/<meeting_id>/registrants", methods=["GET"])
@require_auth
def list_meeting_registrants(meeting_id):
    """List meeting registrants. Query: page_size, next_page_token, status."""
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found"}}), 404
    registrants = m.get("registrants", [])
    page_size = min(int(request.args.get("page_size", 30)), 300)
    page_number = max(1, int(request.args.get("page_number", 1)))
    total = len(registrants)
    start = (page_number - 1) * page_size
    page_reg = registrants[start : start + page_size]
    return jsonify({
        "registrants": page_reg,
        "page_count": max(1, (total + page_size - 1) // page_size),
        "page_size": page_size,
        "total_records": total,
        "next_page_token": generate_random_string(32) if start + page_size < total else "",
    })


@meetings_bp.route("/meetings/<meeting_id>/registrants", methods=["POST"])
@require_auth
def add_meeting_registrants(meeting_id):
    """Add meeting registrants. Body: registrants[].email, registrants[].first_name, registrants[].last_name."""
    data = request.get_json() or {}
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found"}}), 404
    regs = data.get("registrants", [])
    added = [{"id": generate_random_string(22), "email": r.get("email"), "first_name": r.get("first_name"), "last_name": r.get("last_name")} for r in regs]
    return jsonify({"registrants": added, "id": meeting_id, "start_url": f"{BASE_URL}/s/{meeting_id}"}), 201


@meetings_bp.route("/meetings/<meeting_id>/registrants/status", methods=["PATCH"])
@require_auth
def update_meeting_registrants_status(meeting_id):
    """Update registrant status. Body: action (approve/deny), registrants[].id."""
    data = request.get_json() or {}
    action = data.get("action", "approve")
    return jsonify({"id": meeting_id, "registrants": data.get("registrants", [])}), 200


# ---- Meeting livestream (Zoom API) ----
@meetings_bp.route("/meetings/<meeting_id>/livestream", methods=["GET"])
@require_auth
def get_meeting_livestream(meeting_id):
    """Get meeting livestream settings."""
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found"}}), 404
    return jsonify({"stream_url": "", "stream_key": "", "page_url": ""})


@meetings_bp.route("/meetings/<meeting_id>/livestream", methods=["PATCH"])
@require_auth
def update_meeting_livestream(meeting_id):
    """Update meeting livestream. Body: stream_url, stream_key, page_url."""
    data = request.get_json() or {}
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found"}}), 404
    return jsonify({"stream_url": data.get("stream_url", ""), "stream_key": data.get("stream_key", ""), "page_url": data.get("page_url", "")}), 200


# ---- Past meeting instances (recurring) ----
@meetings_bp.route("/past_meetings/<meeting_id>/instances", methods=["GET"])
@require_auth
def get_past_meeting_instances(meeting_id):
    """List past meeting instances (recurring). Returns single instance if one-off."""
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found"}}), 404
    return jsonify({"meetings": [{"uuid": m.get("uuid", meeting_id), "start_time": m.get("start_time", ""), "id": m.get("id", meeting_id)}]})