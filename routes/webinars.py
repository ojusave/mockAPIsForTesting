"""
Zoom Webinars API. Mirrors Zoom REST: users/:userId/webinars, webinars/:webinarId, past_webinars.
"""
from flask import Blueprint, jsonify, request
from helpers import generate_random_string, BASE_URL
from config import DEFAULT_DATE_FROM, DEFAULT_DATE_TO, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from cache_config import cache
from models.auth import require_auth
from data_store import (
    load_webinar,
    get_webinars_for_user,
    get_participants_for_webinar,
    load_user,
)
import datetime

webinars_bp = Blueprint("webinars", __name__)


def _webinar_to_response(w):
    """Return Zoom webinar shape for GET (exclude participants for list/detail)."""
    if not w:
        return None
    return {k: v for k, v in w.items() if k != "participants"}


@webinars_bp.route("/users/<user_id>/webinars", methods=["GET"])
@require_auth
def list_webinars(user_id):
    """List webinars for user. Query: from, to (YYYY-MM-DD), page_size, page_number."""
    from_date = request.args.get("from", DEFAULT_DATE_FROM)
    to_date = request.args.get("to", DEFAULT_DATE_TO)
    page_size = min(int(request.args.get("page_size", DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)
    page_number = max(1, int(request.args.get("page_number", 1)))
    try:
        datetime.datetime.strptime(from_date, "%Y-%m-%d")
        datetime.datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": {"code": "400", "message": "Invalid date format", "details": "Use YYYY-MM-DD"}}), 400
    webinars = get_webinars_for_user(user_id, from_date=from_date, to_date=to_date)
    total = len(webinars)
    start = (page_number - 1) * page_size
    page_webinars = webinars[start : start + page_size]
    return jsonify({
        "page_size": page_size,
        "page_number": page_number,
        "total_records": total,
        "next_page_token": generate_random_string(16) if start + page_size < total else "",
        "webinars": page_webinars,
    })


@webinars_bp.route("/users/<user_id>/webinars", methods=["POST"])
@require_auth
def create_webinar(user_id):
    """Create a webinar. Body: topic, start_time, duration, timezone, agenda, password, settings."""
    data = request.get_json() or {}
    topic = data.get("topic", "My Webinar")
    webinar_id = generate_random_string(22)
    start_str = data.get("start_time")
    if start_str:
        try:
            start = datetime.datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            start = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    else:
        start = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    duration = int(data.get("duration", 60))
    payload = {
        "id": webinar_id,
        "uuid": webinar_id,
        "host_id": user_id,
        "topic": topic,
        "type": 5,
        "start_time": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration": duration,
        "timezone": data.get("timezone", "America/New_York"),
        "created_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "join_url": f"{BASE_URL}/w/{webinar_id}",
        "start_url": f"{BASE_URL}/s/{webinar_id}",
        "password": data.get("password") or generate_random_string(8),
        "agenda": data.get("agenda", ""),
        "settings": data.get("settings") or {},
    }
    return jsonify(payload), 201


@webinars_bp.route("/webinars/<webinar_id>", methods=["GET"])
@require_auth
@cache.memoize(timeout=3600)
def get_webinar(webinar_id):
    """Get webinar by ID."""
    w = load_webinar(webinar_id)
    if not w:
        return jsonify({"error": {"code": "404", "message": "Webinar not found", "details": f"No webinar with id: {webinar_id}"}}), 404
    return jsonify(_webinar_to_response(w))


@webinars_bp.route("/users/<user_id>/webinars/<webinar_id>", methods=["GET"])
@require_auth
def get_user_webinar(user_id, webinar_id):
    """Get webinar (with host)."""
    w = load_webinar(webinar_id)
    if not w:
        return jsonify({"error": {"code": "404", "message": "Webinar not found", "details": f"No webinar with id: {webinar_id}"}}), 404
    if w.get("host_id") != user_id:
        return jsonify({"error": {"code": "404", "message": "Webinar not found for this user"}}), 404
    return jsonify(_webinar_to_response(w))


@webinars_bp.route("/users/<user_id>/webinars/<webinar_id>", methods=["PATCH"])
@require_auth
def update_webinar(user_id, webinar_id):
    """Update webinar. Body: topic, start_time, duration, timezone, agenda, password, settings."""
    data = request.get_json() or {}
    cache.delete_memoized(get_webinar, webinar_id)
    w = load_webinar(webinar_id)
    if not w:
        return jsonify({"error": {"code": "404", "message": "Webinar not found", "details": f"No webinar with id: {webinar_id}"}}), 404
    out = dict(_webinar_to_response(w))
    for key in ("topic", "start_time", "duration", "timezone", "agenda", "password"):
        if key in data:
            out[key] = data[key]
    if "settings" in data:
        out["settings"] = dict(out.get("settings", {}), **data["settings"])
    return jsonify(out), 200


@webinars_bp.route("/users/<user_id>/webinars/<webinar_id>", methods=["DELETE"])
@require_auth
def delete_webinar(user_id, webinar_id):
    """Delete a webinar."""
    cache.delete_memoized(get_webinar, webinar_id)
    w = load_webinar(webinar_id)
    if not w:
        return jsonify({"error": {"code": "404", "message": "Webinar not found"}}), 404
    return "", 204


@webinars_bp.route("/past_webinars/<webinar_id>/participants", methods=["GET"])
@require_auth
def get_past_webinar_participants(webinar_id):
    """List past webinar participants. Query: page_size, page_number."""
    w = load_webinar(webinar_id)
    if not w:
        return jsonify({"error": {"code": "404", "message": "Webinar not found", "details": f"No webinar with id: {webinar_id}"}}), 404
    participants = get_participants_for_webinar(webinar_id)
    page_size = min(int(request.args.get("page_size", 30)), 300)
    page_number = max(1, int(request.args.get("page_number", 1)))
    total = len(participants)
    start = (page_number - 1) * page_size
    page_part = participants[start : start + page_size]
    return jsonify({
        "next_page_token": generate_random_string(32) if start + page_size < total else "",
        "page_count": max(1, (total + page_size - 1) // page_size),
        "page_size": page_size,
        "total_records": total,
        "participants": page_part,
    })


@webinars_bp.route("/past_webinars/<webinar_id>/instances", methods=["GET"])
@require_auth
def get_past_webinar_instances(webinar_id):
    """List past webinar instances (recurring). Returns single instance if one-off."""
    w = load_webinar(webinar_id)
    if not w:
        return jsonify({"error": {"code": "404", "message": "Webinar not found"}}), 404
    # Mock: return one instance (start_time) for this webinar
    return jsonify({
        "instances": [{"start_time": w.get("start_time", ""), "uuid": w.get("uuid", webinar_id)}],
    })


# ---- Webinar polls (Zoom API: developers.zoom.us/docs/api/) ----
@webinars_bp.route("/webinars/<webinar_id>/polls", methods=["GET"])
@require_auth
def list_webinar_polls(webinar_id):
    """List webinar polls."""
    w = load_webinar(webinar_id)
    if not w:
        return jsonify({"error": {"code": "404", "message": "Webinar not found"}}), 404
    return jsonify({"polls": w.get("polls", [])})


@webinars_bp.route("/webinars/<webinar_id>/polls", methods=["POST"])
@require_auth
def create_webinar_poll(webinar_id):
    """Create webinar poll. Body: title, questions."""
    data = request.get_json() or {}
    w = load_webinar(webinar_id)
    if not w:
        return jsonify({"error": {"code": "404", "message": "Webinar not found"}}), 404
    poll_id = generate_random_string(16)
    poll = {"id": poll_id, "title": data.get("title", "Poll"), "questions": data.get("questions", [])}
    return jsonify(poll), 201


@webinars_bp.route("/webinars/<webinar_id>/polls/<poll_id>", methods=["GET"])
@require_auth
def get_webinar_poll(webinar_id, poll_id):
    """Get webinar poll by ID."""
    w = load_webinar(webinar_id)
    if not w:
        return jsonify({"error": {"code": "404", "message": "Webinar not found"}}), 404
    polls = w.get("polls", [])
    poll = next((p for p in polls if p.get("id") == poll_id), None)
    if not poll:
        return jsonify({"error": {"code": "404", "message": "Poll not found"}}), 404
    return jsonify(poll)


@webinars_bp.route("/webinars/<webinar_id>/polls/<poll_id>", methods=["PATCH"])
@require_auth
def update_webinar_poll(webinar_id, poll_id):
    """Update webinar poll. Body: title, questions."""
    data = request.get_json() or {}
    poll = {"id": poll_id, "title": data.get("title", "Poll"), "questions": data.get("questions", [])}
    return jsonify(poll), 200


@webinars_bp.route("/webinars/<webinar_id>/polls/<poll_id>", methods=["DELETE"])
@require_auth
def delete_webinar_poll(webinar_id, poll_id):
    """Delete webinar poll."""
    w = load_webinar(webinar_id)
    if not w:
        return jsonify({"error": {"code": "404", "message": "Webinar not found"}}), 404
    return "", 204


# ---- Webinar registrants (Zoom API) ----
@webinars_bp.route("/webinars/<webinar_id>/registrants", methods=["GET"])
@require_auth
def list_webinar_registrants(webinar_id):
    """List webinar registrants. Query: page_size, status."""
    w = load_webinar(webinar_id)
    if not w:
        return jsonify({"error": {"code": "404", "message": "Webinar not found"}}), 404
    registrants = w.get("registrants", [])
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


@webinars_bp.route("/webinars/<webinar_id>/registrants", methods=["POST"])
@require_auth
def add_webinar_registrants(webinar_id):
    """Add webinar registrants. Body: registrants[].email, first_name, last_name."""
    data = request.get_json() or {}
    w = load_webinar(webinar_id)
    if not w:
        return jsonify({"error": {"code": "404", "message": "Webinar not found"}}), 404
    regs = data.get("registrants", [])
    added = [{"id": generate_random_string(22), "email": r.get("email"), "first_name": r.get("first_name"), "last_name": r.get("last_name")} for r in regs]
    return jsonify({"registrants": added, "id": webinar_id}), 201


@webinars_bp.route("/webinars/<webinar_id>/registrants/status", methods=["PATCH"])
@require_auth
def update_webinar_registrants_status(webinar_id):
    """Update webinar registrant status. Body: action (approve/deny), registrants[].id."""
    data = request.get_json() or {}
    return jsonify({"id": webinar_id, "registrants": data.get("registrants", [])}), 200
