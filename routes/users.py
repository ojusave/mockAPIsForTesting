from flask import Blueprint, jsonify, request
from helpers import generate_user_id
from config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from models.auth import require_auth
from cache_config import cache
from data_store import list_user_ids, load_user, save_user
import random
import os
from datetime import datetime, timedelta

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["GET"])
@require_auth
def get_data():
    """List users from data/users/ (Zoom-style). Query: page_size, page_number, status."""
    page_size = min(int(request.args.get("page_size", DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)
    page_number = max(1, int(request.args.get("page_number", 1)))
    status_filter = request.args.get("status")
    all_ids = list_user_ids()
    users = []
    for uid in all_ids:
        u = load_user(uid)
        if not u:
            continue
        if status_filter and status_filter in ("active", "inactive", "pending") and u.get("status") != status_filter:
            continue
        users.append(u)
    total_records = len(users)
    start = (page_number - 1) * page_size
    page_users = users[start : start + page_size]
    response_data = {
        "next_page_token": os.urandom(16).hex() if start + page_size < total_records else "",
        "page_count": max(1, (total_records + page_size - 1) // page_size),
        "page_number": page_number,
        "page_size": page_size,
        "total_records": total_records,
        "users": page_users,
    }
    return jsonify(response_data)


@users_bp.route("/users", methods=["POST"])
@require_auth
def create_user():
    """Create a new user (Zoom-style). Accepts: email, first_name, last_name, type, display_name, password."""
    data = request.get_json() or {}
    if not data.get("email") or not data.get("first_name") or not data.get("last_name"):
        return jsonify({
            "error": {"code": "400", "message": "Validation failed", "details": "email, first_name, last_name are required"}
        }), 400
    user_id = data.get("id") or generate_user_id()
    created = (datetime.utcnow() - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    display = data.get("display_name") or f"{data['first_name']} {data['last_name']}"
    user = {
        "id": user_id,
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "email": data["email"],
        "type": data.get("type", 1),
        "created_at": created,
        "status": "pending",
        "display_name": display,
    }
    if data.get("password") is not None:
        user["password"] = "[REDACTED]"
    save_user(user_id, user)
    return jsonify(user), 201


@users_bp.route("/users/<user_id>", methods=["DELETE"])
@require_auth
def delete_user(user_id):
    """Delete a user (Zoom-style)."""
    cache.delete_memoized(get_user, user_id)
    cache.delete("list_users")
    return "", 204


@users_bp.route("/users/me", methods=["GET"])
@require_auth
def get_current_user():
    """Get current user (Zoom API: GET /v2/users/me). Mock: returns first user from data store."""
    all_ids = list_user_ids()
    if not all_ids:
        return jsonify({"error": {"code": "404", "message": "User not found", "details": "No users in data store"}}), 404
    user = load_user(all_ids[0])
    if not user:
        return jsonify({"error": {"code": "404", "message": "User not found"}}), 404
    return jsonify(user)


@users_bp.route("/users/<user_id>", methods=["GET"])
@cache.memoize(timeout=3600)
@require_auth
def get_user(user_id):
    """Get user from data/users/<user_id>.json (Zoom-style). Returns 404 if not found."""
    user = load_user(user_id)
    if not user:
        return jsonify({"error": {"code": "404", "message": "User not found", "details": f"No user with id: {user_id}"}}), 404
    # Return Zoom user object (exclude internal keys like meeting_ids if desired; Zoom often includes them in profile)
    return jsonify(user)

@users_bp.route("/users/<user_id>/status", methods=["PUT"])
@require_auth
def update_user_status(user_id):
    """Update a user's status. Body: { \"action\": \"activate\" | \"deactivate\" | \"clock_in\" | \"clock_out\" }."""
    data = request.get_json() or {}
    action = data.get("action")
    if not action:
        return jsonify({"error": {"code": "400", "message": "Validation failed", "details": "action is required"}}), 400
    if action not in ("activate", "deactivate", "clock_in", "clock_out"):
        return jsonify({"error": {"code": "400", "message": "Invalid action", "details": "action must be one of: activate, deactivate, clock_in, clock_out"}}), 400
    return jsonify({"id": user_id, "status": "active" if action == "activate" else "inactive"}), 200


@users_bp.route("/users/<user_id>/token", methods=["GET"])
@require_auth
def get_user_token(user_id):
    """Get a user's Zoom token or ZAK. Query: type=token|zak, ttl=seconds."""
    token_type = request.args.get("type", "token")
    ttl = int(request.args.get("ttl", 7200))
    if token_type not in ("token", "zak"):
        return jsonify({"error": {"code": "400", "message": "Invalid token type", "details": "type must be token or zak"}}), 400
    response = {"token": "6IjAwMDAwMSIsInptX3NrbSI6InptX", "type": token_type}
    if ttl:
        response["ttl"] = ttl
    return jsonify(response)

@users_bp.route("/users/<user_id>/token", methods=["DELETE"]) 
@require_auth
def revoke_user_token(user_id):
    """Revoke a user's SSO token"""
    # Mock response - return 204 for successful deletion
    return '', 204

@users_bp.route("/users/<user_id>/settings", methods=["GET"])
@require_auth
def get_user_settings(user_id):
    """Get user settings (Zoom API: schedule_meeting, in_meeting, email_notification, etc.)."""
    u = load_user(user_id)
    if not u:
        return jsonify({"error": {"code": "404", "message": "User not found"}}), 404
    settings = u.get("settings", {})
    if not settings:
        settings = {
            "schedule_meeting": {"host_video": True, "participant_video": False, "join_before_host": False},
            "in_meeting": {"mute_upon_entry": True, "waiting_room": True},
            "email_notification": {"jbh_reminder": True, "cancel_reminder": True},
        }
    return jsonify(settings)


@users_bp.route("/users/<user_id>/settings", methods=["PATCH"])
@require_auth
def update_user_settings(user_id):
    """Update user settings. Body: schedule_meeting, in_meeting, email_notification, etc."""
    data = request.get_json() or {}
    u = load_user(user_id)
    if not u:
        return jsonify({"error": {"code": "404", "message": "User not found"}}), 404
    current = u.get("settings", {})
    merged = dict(current, **{k: v for k, v in data.items() if v is not None})
    return jsonify(merged), 200


@users_bp.route("/users/<user_id>/settings/virtual_backgrounds", methods=["POST"])
@require_auth
def upload_virtual_background(user_id):
    """Upload virtual background. Form: file=...; optional JSON/form: is_default, name, type."""
    data = request.form or request.get_json() or {}
    file = request.files.get("file")
    name = (file.filename if file else None) or data.get("name", "background.png")
    is_default = data.get("is_default", "true").lower() in ("true", "1", "yes")
    ftype = data.get("type", "image")
    response = {
        "id": "_l0MP1U7Qn2JgJ4oEJbVZQ",
        "is_default": is_default,
        "name": name,
        "size": 7221,
        "type": ftype,
    }
    return jsonify(response), 201


@users_bp.route("/users/<user_id>/settings/virtual_backgrounds", methods=["DELETE"])
@require_auth
def delete_virtual_backgrounds(user_id):
    """Delete virtual background files. Query: file_ids=id1,id2 (comma-separated)."""
    file_ids = request.args.get("file_ids")
    if not file_ids:
        return jsonify({"error": {"code": "400", "message": "file_ids required", "details": "Query param file_ids (comma-separated) is required"}}), 400
    return "", 204

@users_bp.route("/users/<user_id>", methods=["PATCH"])
@require_auth
def update_user(user_id):
    """Update user. Body merged into profile from data/users/<user_id>.json; 404 if user not in data."""
    data = request.get_json() or {}
    cache.delete_memoized(get_user, user_id)
    base = load_user(user_id)
    if not base:
        return jsonify({"error": {"code": "404", "message": "User not found", "details": f"No user with id: {user_id}"}}), 404
    base = dict(base)
    allowed = ("first_name", "last_name", "display_name", "timezone", "language", "dept", "phone_number", "type", "company", "job_title", "phone_country")
    for key in allowed:
        if key in data:
            base[key] = data[key]
    if "first_name" in data or "last_name" in data:
        base["display_name"] = base.get("display_name") or f"{base.get('first_name', '')} {base.get('last_name', '')}"
    save_user(user_id, base)
    return jsonify(base), 200