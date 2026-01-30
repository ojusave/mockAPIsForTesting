"""
Zoom Reports API. Mirrors Zoom REST: report/users, report/meetings, report/webinars, metrics.
"""
from flask import Blueprint, jsonify, request
from helpers import generate_random_string
from config import DEFAULT_DATE_FROM, DEFAULT_DATE_TO, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from models.auth import require_auth
from data_store import load_user, list_user_ids, load_meeting, get_participants_for_meeting, load_webinar, get_participants_for_webinar, get_meetings_for_user
import datetime

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/report/users", methods=["GET"])
@require_auth
def report_users():
    """Get active/inactive host report. Query: type (active|inactive), from, to, page_size, page_number."""
    report_type = request.args.get("type", "active")
    from_date = request.args.get("from", DEFAULT_DATE_FROM)
    to_date = request.args.get("to", DEFAULT_DATE_TO)
    page_size = min(int(request.args.get("page_size", DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)
    page_number = max(1, int(request.args.get("page_number", 1)))
    user_ids = list_user_ids()
    users = []
    for uid in user_ids:
        u = load_user(uid)
        if not u:
            continue
        # Mock: active = status active, inactive = status inactive
        if report_type == "active" and u.get("status") != "active":
            continue
        if report_type == "inactive" and u.get("status") == "active":
            continue
        users.append({
            "id": u.get("id"),
            "email": u.get("email"),
            "first_name": u.get("first_name"),
            "last_name": u.get("last_name"),
            "type": u.get("type"),
            "created_at": u.get("created_at"),
            "last_login_time": u.get("last_login_time"),
        })
    total = len(users)
    start = (page_number - 1) * page_size
    page_users = users[start : start + page_size]
    return jsonify({
        "from": from_date,
        "to": to_date,
        "page_size": page_size,
        "page_number": page_number,
        "total_records": total,
        "next_page_token": generate_random_string(16) if start + page_size < total else "",
        "users": page_users,
    })


@reports_bp.route("/report/meetings/<meeting_id>/participants", methods=["GET"])
@require_auth
def report_meeting_participants(meeting_id):
    """Get meeting participant report. Query: page_size, next_page_token."""
    m = load_meeting(meeting_id)
    if not m:
        return jsonify({"error": {"code": "404", "message": "Meeting not found", "details": f"No meeting with id: {meeting_id}"}}), 404
    participants = get_participants_for_meeting(meeting_id)
    page_size = min(int(request.args.get("page_size", 30)), 300)
    page_number = max(1, int(request.args.get("page_number", 1)))
    total = len(participants)
    start = (page_number - 1) * page_size
    page_part = participants[start : start + page_size]
    return jsonify({
        "meeting_id": meeting_id,
        "next_page_token": generate_random_string(32) if start + page_size < total else "",
        "page_count": max(1, (total + page_size - 1) // page_size),
        "page_size": page_size,
        "total_records": total,
        "participants": page_part,
    })


@reports_bp.route("/report/webinars/<webinar_id>/participants", methods=["GET"])
@require_auth
def report_webinar_participants(webinar_id):
    """Get webinar participant report. Query: page_size, page_number."""
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
        "webinar_id": webinar_id,
        "next_page_token": generate_random_string(32) if start + page_size < total else "",
        "page_count": max(1, (total + page_size - 1) // page_size),
        "page_size": page_size,
        "total_records": total,
        "participants": page_part,
    })


@reports_bp.route("/metrics/meetings", methods=["GET"])
@require_auth
def metrics_meetings():
    """List meetings for metrics/reporting. Query: from, to, type, page_size, next_page_token."""
    from_date = request.args.get("from", DEFAULT_DATE_FROM)
    to_date = request.args.get("to", DEFAULT_DATE_TO)
    page_size = min(int(request.args.get("page_size", DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)
    page_number = max(1, int(request.args.get("page_number", 1)))
    meetings = []
    for uid in list_user_ids():
        meetings.extend(get_meetings_for_user(uid, from_date=from_date, to_date=to_date))
    total = len(meetings)
    start = (page_number - 1) * page_size
    page_meetings = meetings[start : start + page_size]
    return jsonify({
        "from": from_date,
        "to": to_date,
        "page_size": page_size,
        "next_page_token": generate_random_string(16) if start + page_size < total else "",
        "meetings": page_meetings,
    })


@reports_bp.route("/report/daily", methods=["GET"])
@require_auth
def report_daily():
    """Get daily report. Query: year, month. Mock: returns summary counts."""
    year = request.args.get("year", "2026")
    month = request.args.get("month", "1")
    return jsonify({
        "year": int(year),
        "month": int(month),
        "dates": [{"date": f"{year}-{month.zfill(2)}-{d:02d}", "meetings": 2, "participants": 10, "new_users": 0} for d in range(1, min(4, 29))],
    })
