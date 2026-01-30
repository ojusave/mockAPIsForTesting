"""
Zoom Roles API stubs. Mirrors Zoom REST: roles.
"""
from flask import Blueprint, jsonify, request
from models.auth import require_auth
from helpers import generate_random_string

roles_bp = Blueprint("roles", __name__)


@roles_bp.route("/roles", methods=["GET"])
@require_auth
def list_roles():
    """List roles. Query: page_size, next_page_token."""
    page_size = min(int(request.args.get("page_size", 30)), 300)
    return jsonify({
        "page_size": page_size,
        "next_page_token": "",
        "roles": [
            {"id": "1", "name": "owner", "description": "Account owner", "total_members": 1},
            {"id": "2", "name": "admin", "description": "Administrator", "total_members": 0},
            {"id": "3", "name": "member", "description": "Member", "total_members": 2},
        ],
    })


@roles_bp.route("/roles/<role_id>", methods=["GET"])
@require_auth
def get_role(role_id):
    """Get role by ID."""
    return jsonify({"id": role_id, "name": "member", "description": "Member", "total_members": 0})


@roles_bp.route("/roles/<role_id>/members", methods=["GET"])
@require_auth
def list_role_members(role_id):
    """List members with role. Query: page_size, next_page_token."""
    return jsonify({"page_size": 30, "next_page_token": "", "members": []})


@roles_bp.route("/roles/<role_id>/members", methods=["POST"])
@require_auth
def assign_role(role_id):
    """Assign role to members. Body: members[].id, members[].email."""
    data = request.get_json() or {}
    return jsonify({"ids": [m.get("id") or generate_random_string(22) for m in data.get("members", [])]}), 201


@roles_bp.route("/roles/<role_id>/members/<member_id>", methods=["DELETE"])
@require_auth
def remove_role_member(role_id, member_id):
    """Remove member from role."""
    return "", 204
