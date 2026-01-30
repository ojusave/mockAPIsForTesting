from flask import Blueprint, jsonify, request
from helpers import generate_random_string
from config import DEFAULT_DATE_FROM, DEFAULT_DATE_TO, MAX_PAGE_SIZE
from models.auth import require_auth
from data_store import get_recordings_for_user, get_recordings_for_meeting, load_meeting
import datetime
import logging

recordings_bp = Blueprint("recordings", __name__)
logger = logging.getLogger(__name__)


@recordings_bp.route("/users/<user_id>/recordings", methods=["GET"])
@require_auth
def get_user_recordings(user_id):
    """List user recordings from data store. Query: from, to (YYYY-MM-DD), page_size, page_number, trash."""
    from_date = request.args.get("from", DEFAULT_DATE_FROM)
    to_date = request.args.get("to", DEFAULT_DATE_TO)
    page_size = min(int(request.args.get("page_size", 30)), MAX_PAGE_SIZE)
    page_number = max(1, int(request.args.get("page_number", 1)))
    trash = request.args.get("trash", "false").lower() in ("true", "1", "yes")
    try:
        datetime.datetime.strptime(from_date, "%Y-%m-%d")
        datetime.datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": {"code": "400", "message": "Invalid date format", "details": "Use YYYY-MM-DD for from and to"}}), 400
    recordings = get_recordings_for_user(user_id, from_date=from_date, to_date=to_date)
    total = len(recordings)
    start = (page_number - 1) * page_size
    page_recordings = recordings[start : start + page_size]
    response_data = {
        "from": from_date,
        "to": to_date,
        "page_size": page_size,
        "page_number": page_number,
        "total_records": total,
        "page_count": max(1, (total + page_size - 1) // page_size) if total else 1,
        "next_page_token": generate_random_string(16) if start + page_size < total else "",
        "meetings": page_recordings,
    }
    if trash:
        response_data["trash"] = False
    return jsonify(response_data)


@recordings_bp.route("/meetings/<meeting_id>/recordings", methods=["GET"])
@require_auth
def get_meeting_recordings(meeting_id):
    """Get recordings for a meeting from data store. Query: trash (boolean)."""
    trash = request.args.get("trash", "false").lower() in ("true", "1", "yes")
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found", "details": f"No meeting with id: {meeting_id}"}}), 404
    recording_files = get_recordings_for_meeting(meeting_id)
    out = {"meeting_id": meeting_id, "meeting_uuid": m.get("uuid") or meeting_id, "recording_files": recording_files}
    if trash:
        out["trash"] = False
    return jsonify(out)


@recordings_bp.route("/meetings/<meeting_id>/recordings/<recording_id>", methods=["DELETE"])
@require_auth
def delete_meeting_recording(meeting_id, recording_id):
    """Delete or move to trash. Body: { \"action\": \"trash\" | \"delete\" } (optional)."""
    data = request.get_json() or {}
    action = data.get("action", "delete")
    return "", 204
