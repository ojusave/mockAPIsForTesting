"""
Zoom Rooms API. Source of truth: data/rooms.json.
"""
from flask import Blueprint, jsonify, request
from models.auth import require_auth
from helpers import generate_random_string, BASE_URL
from data_store import load_rooms, save_rooms

rooms_bp = Blueprint("rooms", __name__)


@rooms_bp.route("/rooms", methods=["GET"])
@require_auth
def list_rooms():
    """List Zoom Rooms. Query: page_size, next_page_token, status, location_id."""
    page_size = min(int(request.args.get("page_size", 30)), 300)
    page_number = max(1, int(request.args.get("page_number", 1)))
    status_filter = request.args.get("status")
    location_id = request.args.get("location_id")
    rooms = load_rooms()
    filtered = rooms
    if status_filter:
        filtered = [r for r in filtered if r.get("status") == status_filter]
    if location_id:
        filtered = [r for r in filtered if r.get("location_id") == location_id]
    total = len(filtered)
    start = (page_number - 1) * page_size
    page = filtered[start : start + page_size]
    return jsonify({
        "rooms": page,
        "page_size": page_size,
        "next_page_token": generate_random_string(16) if start + page_size < total else "",
        "total_records": total,
    })


@rooms_bp.route("/rooms", methods=["POST"])
@require_auth
def create_room():
    """Create Zoom Room. Body: name, type, location_id, calendar_name."""
    data = request.get_json() or {}
    room_id = generate_random_string(16)
    room = {
        "id": room_id,
        "name": data.get("name", "New Room"),
        "type": data.get("type", "Zoom Room"),
        "location_id": data.get("location_id", ""),
        "calendar_name": data.get("calendar_name", ""),
        "status": "Offline",
    }
    rooms = load_rooms()
    rooms.append(room)
    save_rooms(rooms)
    return jsonify(room), 201


@rooms_bp.route("/rooms/<room_id>", methods=["GET"])
@require_auth
def get_room(room_id):
    """Get Zoom Room by ID."""
    rooms = load_rooms()
    room = next((r for r in rooms if r.get("id") == room_id), None)
    if not room:
        return jsonify({"error": {"code": "404", "message": "Room not found"}}), 404
    return jsonify(room)


@rooms_bp.route("/rooms/<room_id>", methods=["PATCH"])
@require_auth
def update_room(room_id):
    """Update Zoom Room. Body: name, calendar_name, status."""
    data = request.get_json() or {}
    rooms = load_rooms()
    idx = next((i for i, r in enumerate(rooms) if r.get("id") == room_id), None)
    if idx is None:
        return jsonify({"error": {"code": "404", "message": "Room not found"}}), 404
    out = dict(rooms[idx])
    for key in ("name", "calendar_name", "status", "location_id"):
        if key in data:
            out[key] = data[key]
    rooms[idx] = out
    save_rooms(rooms)
    return jsonify(out), 200


@rooms_bp.route("/rooms/<room_id>", methods=["DELETE"])
@require_auth
def delete_room(room_id):
    """Delete Zoom Room."""
    rooms = load_rooms()
    rooms = [r for r in rooms if r.get("id") != room_id]
    save_rooms(rooms)
    return "", 204


@rooms_bp.route("/rooms/<room_id>/meetings", methods=["GET"])
@require_auth
def list_room_meetings(room_id):
    """List meetings for a Zoom Room. Query: from, to."""
    rooms = load_rooms()
    room = next((r for r in rooms if r.get("id") == room_id), None)
    if not room:
        return jsonify({"error": {"code": "404", "message": "Room not found"}}), 404
    return jsonify({"meetings": [], "room_id": room_id})


@rooms_bp.route("/rooms/<room_id>/meetings", methods=["POST"])
@require_auth
def create_room_meeting(room_id):
    """Create a meeting for a Zoom Room. Body: topic, start_time, duration."""
    data = request.get_json() or {}
    rooms = load_rooms()
    room = next((r for r in rooms if r.get("id") == room_id), None)
    if not room:
        return jsonify({"error": {"code": "404", "message": "Room not found"}}), 404
    meeting_id = generate_random_string(22)
    meeting = {
        "id": meeting_id,
        "uuid": meeting_id,
        "topic": data.get("topic", "Room Meeting"),
        "start_time": data.get("start_time", "2026-01-15T14:00:00Z"),
        "duration": data.get("duration", 60),
        "join_url": f"{BASE_URL}/j/{meeting_id}",
    }
    return jsonify(meeting), 201
