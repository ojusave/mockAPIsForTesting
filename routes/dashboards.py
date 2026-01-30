"""
Zoom Dashboards / Metrics API stubs. Mirrors Zoom REST: metrics, dashboards.
"""
from flask import Blueprint, jsonify, request
from helpers import generate_random_string
from config import DEFAULT_DATE_FROM, DEFAULT_DATE_TO
from models.auth import require_auth
from data_store import get_participants_for_meeting

dashboards_bp = Blueprint("dashboards", __name__)


@dashboards_bp.route("/metrics/meetings/<meeting_id>/participants", methods=["GET"])
@require_auth
def metrics_meeting_participants(meeting_id):
    """Get meeting participants QoS/metrics from data store. Query: type (past|live), page_size."""
    page_size = min(int(request.args.get("page_size", 30)), 300)
    page_number = max(1, int(request.args.get("page_number", 1)))
    participants = get_participants_for_meeting(meeting_id)
    total = len(participants)
    start = (page_number - 1) * page_size
    page_part = participants[start : start + page_size]
    return jsonify({
        "meeting_id": meeting_id,
        "page_size": page_size,
        "page_number": page_number,
        "total_records": total,
        "next_page_token": generate_random_string(32) if start + page_size < total else "",
        "participants": page_part,
    })


@dashboards_bp.route("/metrics/webinars/<webinar_id>/participants", methods=["GET"])
@require_auth
def metrics_webinar_participants(webinar_id):
    """Get webinar participants QoS/metrics from data store."""
    from data_store import get_participants_for_webinar
    page_size = min(int(request.args.get("page_size", 30)), 300)
    page_number = max(1, int(request.args.get("page_number", 1)))
    participants = get_participants_for_webinar(webinar_id)
    total = len(participants)
    start = (page_number - 1) * page_size
    page_part = participants[start : start + page_size]
    return jsonify({
        "webinar_id": webinar_id,
        "page_size": page_size,
        "page_number": page_number,
        "total_records": total,
        "next_page_token": generate_random_string(32) if start + page_size < total else "",
        "participants": page_part,
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
