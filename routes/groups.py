"""
Zoom Groups API stubs. Mirrors Zoom REST: groups (IM groups).
"""
from flask import Blueprint, jsonify, request
from models.auth import require_auth
from helpers import generate_random_string

groups_bp = Blueprint("groups", __name__)


@groups_bp.route("/groups", methods=["GET"])
@require_auth
def list_groups():
    """List groups. Query: page_size, next_page_token."""
    page_size = min(int(request.args.get("page_size", 30)), 300)
    return jsonify({
        "page_size": page_size,
        "next_page_token": "",
        "groups": [
            {"id": "g1", "name": "All Users", "total_members": 3},
        ],
    })


@groups_bp.route("/groups", methods=["POST"])
@require_auth
def create_group():
    """Create group. Body: name."""
    data = request.get_json() or {}
    gid = generate_random_string(16)
    return jsonify({"id": gid, "name": data.get("name", "New Group"), "total_members": 0}), 201


@groups_bp.route("/groups/<group_id>", methods=["GET"])
@require_auth
def get_group(group_id):
    """Get group by ID."""
    return jsonify({"id": group_id, "name": "Group", "total_members": 0})


@groups_bp.route("/groups/<group_id>", methods=["PATCH"])
@require_auth
def update_group(group_id):
    """Update group. Body: name."""
    data = request.get_json() or {}
    return jsonify({"id": group_id, "name": data.get("name", "Group"), "total_members": 0}), 200


@groups_bp.route("/groups/<group_id>", methods=["DELETE"])
@require_auth
def delete_group(group_id):
    """Delete group."""
    return "", 204


@groups_bp.route("/groups/<group_id>/members", methods=["GET"])
@require_auth
def list_group_members(group_id):
    """List group members. Query: page_size, next_page_token."""
    return jsonify({"page_size": 30, "next_page_token": "", "members": []})


@groups_bp.route("/groups/<group_id>/members", methods=["POST"])
@require_auth
def add_group_members(group_id):
    """Add members to group. Body: members[].id, members[].email."""
    data = request.get_json() or {}
    return jsonify({"ids": [m.get("id") or generate_random_string(22) for m in data.get("members", [])]}), 201


@groups_bp.route("/groups/<group_id>/members/<member_id>", methods=["DELETE"])
@require_auth
def remove_group_member(group_id, member_id):
    """Remove member from group."""
    return "", 204
