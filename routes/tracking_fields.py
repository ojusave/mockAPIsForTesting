"""
Zoom Tracking Fields API. Source of truth: data/tracking_fields.json.
"""
from flask import Blueprint, jsonify, request
from models.auth import require_auth
from helpers import generate_random_string
from data_store import load_tracking_fields, save_tracking_fields

tracking_fields_bp = Blueprint("tracking_fields", __name__)


@tracking_fields_bp.route("/tracking_fields", methods=["GET"])
@require_auth
def list_tracking_fields():
    """List tracking fields. Query: page_size, next_page_token."""
    page_size = min(int(request.args.get("page_size", 30)), 300)
    page_number = max(1, int(request.args.get("page_number", 1)))
    fields = load_tracking_fields()
    total = len(fields)
    start = (page_number - 1) * page_size
    page = fields[start : start + page_size]
    return jsonify({
        "tracking_fields": page,
        "page_size": page_size,
        "next_page_token": generate_random_string(16) if start + page_size < total else "",
        "total_records": total,
    })


@tracking_fields_bp.route("/tracking_fields", methods=["POST"])
@require_auth
def create_tracking_field():
    """Create tracking field. Body: field, value, visible."""
    data = request.get_json() or {}
    field_id = generate_random_string(16)
    entry = {"id": field_id, "field": data.get("field", ""), "value": data.get("value", ""), "visible": data.get("visible", True)}
    fields = load_tracking_fields()
    fields.append(entry)
    save_tracking_fields(fields)
    return jsonify(entry), 201


@tracking_fields_bp.route("/tracking_fields/<field_id>", methods=["GET"])
@require_auth
def get_tracking_field(field_id):
    """Get tracking field by ID."""
    fields = load_tracking_fields()
    entry = next((f for f in fields if f.get("id") == field_id), None)
    if not entry:
        return jsonify({"error": {"code": "404", "message": "Tracking field not found"}}), 404
    return jsonify(entry)


@tracking_fields_bp.route("/tracking_fields/<field_id>", methods=["PATCH"])
@require_auth
def update_tracking_field(field_id):
    """Update tracking field. Body: field, value, visible."""
    data = request.get_json() or {}
    fields = load_tracking_fields()
    idx = next((i for i, f in enumerate(fields) if f.get("id") == field_id), None)
    if idx is None:
        return jsonify({"error": {"code": "404", "message": "Tracking field not found"}}), 404
    out = dict(fields[idx])
    for key in ("field", "value", "visible"):
        if key in data:
            out[key] = data[key]
    fields[idx] = out
    save_tracking_fields(fields)
    return jsonify(out), 200


@tracking_fields_bp.route("/tracking_fields/<field_id>", methods=["DELETE"])
@require_auth
def delete_tracking_field(field_id):
    """Delete tracking field."""
    fields = load_tracking_fields()
    fields = [f for f in fields if f.get("id") != field_id]
    save_tracking_fields(fields)
    return "", 204
