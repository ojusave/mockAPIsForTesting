"""
Zoom Dashboards / Metrics API stubs. Mirrors Zoom REST: metrics, dashboards.
"""
from flask import Blueprint, jsonify, request
from helpers import generate_random_string
from config import DEFAULT_DATE_FROM, DEFAULT_DATE_TO
from models.auth import require_auth

dashboards_bp = Blueprint("dashboards", __name__)


@dashboards_bp.route("/metrics/meetings/<meeting_id>/participants", methods=["GET"])
@require_auth
def metrics_meeting_participants(meeting_id):
    """Get meeting participants QoS/metrics. Query: type (past|live), page_size."""
    page_size = min(int(request.args.get("page_size", 30)), 300)
    return jsonify({
        "meeting_id": meeting_id,
        "page_size": page_size,
        "next_page_token": "",
        "participants": [
            {"id": "p1", "user_id": "u1", "user_name": "User One", "device": "Windows", "ip_address": "1.2.3.4", "location": "US", "join_time": "2026-01-15T14:00:00Z", "leave_time": "2026-01-15T15:00:00Z", "duration": 3600}
        ],
    })


@dashboards_bp.route("/metrics/webinars/<webinar_id>/participants", methods=["GET"])
@require_auth
def metrics_webinar_participants(webinar_id):
    """Get webinar participants QoS/metrics."""
    return jsonify({
        "webinar_id": webinar_id,
        "page_size": 30,
        "next_page_token": "",
        "participants": [],
    })


@dashboards_bp.route("/metrics/crc", methods=["GET"])
@require_auth
def metrics_crc():
    """Get CRC (Cloud Room Connector) metrics. Query: from, to."""
    from_date = request.args.get("from", DEFAULT_DATE_FROM)
    to_date = request.args.get("to", DEFAULT_DATE_TO)
    return jsonify({"from": from_date, "to": to_date, "crc_ports_usage": []})


@dashboards_bp.route("/metrics/zoom_rooms", methods=["GET"])
@require_auth
def metrics_zoom_rooms():
    """Get Zoom Rooms metrics. Query: from, to, page_size."""
    return jsonify({"from": DEFAULT_DATE_FROM, "to": DEFAULT_DATE_TO, "zoom_rooms": []})
