from flask import Blueprint, jsonify, request
from helpers import generate_random_string
from models.auth import require_auth
import random

qss_bp = Blueprint("qss", __name__)

# In-memory store for mock feedback (Zoom Quality Scoring / QSS)
_feedback_store = {}

def generate_qos_details():
    """Generate random QoS metrics"""
    return {
        "min_bitrate": f"{random.uniform(20, 100):.2f}kbps",
        "avg_bitrate": f"{random.uniform(50, 150):.2f}kbps",
        "max_bitrate": f"{random.uniform(100, 200):.2f}kbps",
        "min_latency": f"{random.randint(50, 100)} ms",
        "avg_latency": f"{random.randint(80, 150)} ms",
        "max_latency": f"{random.randint(120, 200)} ms",
        "min_jitter": f"{random.randint(0, 5)}ms",
        "avg_jitter": f"{random.randint(2, 8)}ms",
        "max_jitter": f"{random.randint(5, 15)}ms",
        "min_loss": f"{random.uniform(0, 0.1):.2f}%",
        "avg_loss": f"{random.uniform(0.1, 0.3):.2f}%",
        "max_loss": f"{random.uniform(0.2, 0.5):.2f}%",
        "resolution": random.choice(["640*480", "1280*720", "1920*1080"]),
        "min_frame_rate": f"{random.randint(10, 15)} fps",
        "avg_frame_rate": f"{random.randint(15, 25)} fps",
        "max_frame_rate": f"{random.randint(25, 30)} fps",
        "zoom_min_cpu_usage": f"{random.randint(0, 5)}%",
        "zoom_avg_cpu_usage": f"{random.randint(5, 15)}%",
        "zoom_max_cpu_usage": f"{random.randint(15, 30)}%",
        "system_max_cpu_usage": f"{random.randint(30, 70)}%"
    }

def generate_qos_data():
    """Generate QoS data for different types"""
    qos_types = [
        "audio_input", "audio_output", "video_input", "video_output",
        "as_input", "as_output", "cpu_usage"
    ]
    return [
        {
            "type": qos_type,
            "details": generate_qos_details()
        }
        for qos_type in random.sample(qos_types, random.randint(3, len(qos_types)))
    ]

@qss_bp.route("/qss/score/<meeting_id>", methods=["GET"])
@require_auth
def get_qss_score(meeting_id):
    """Get quality score. Query: from, to (optional date range)."""
    request.args.get("from")
    request.args.get("to")
    score = round(random.uniform(3.0, 5.0), 1)
    return jsonify({
        "meeting_id": meeting_id,
        "quality_score": score,
        "score_breakdown": {
            "video": round(random.uniform(3.5, 5.0), 1),
            "audio": round(random.uniform(3.5, 5.0), 1),
            "screen_share": round(random.uniform(3.5, 5.0), 1),
        },
    })


@qss_bp.route("/qss/feedback", methods=["POST"])
@require_auth
def submit_qss_feedback():
    """Submit quality feedback (Zoom QSS)."""
    data = request.get_json() or {}
    feedback_id = generate_random_string(22)
    _feedback_store[feedback_id] = {
        "id": feedback_id,
        "meeting_id": data.get("meeting_id", ""),
        "rating": data.get("rating"),
        "comments": data.get("comments", ""),
        "created_at": data.get("created_at"),
    }
    return jsonify(_feedback_store[feedback_id]), 201


@qss_bp.route("/qss/feedback/<feedback_id>", methods=["GET"])
@require_auth
def get_qss_feedback(feedback_id):
    """Get specific feedback by ID."""
    if feedback_id not in _feedback_store:
        return jsonify({"error": {"code": "404", "message": "Feedback not found"}}), 404
    return jsonify(_feedback_store[feedback_id])


@qss_bp.route("/qss/feedback/<feedback_id>", methods=["DELETE"])
@require_auth
def delete_qss_feedback(feedback_id):
    """Delete specific feedback."""
    _feedback_store.pop(feedback_id, None)
    return "", 204


@qss_bp.route("/metrics/meetings/<meeting_id>/participants/qos_summary", methods=["GET"])
@require_auth
def get_meeting_participants_qos(meeting_id):
    """Query: page_size, next_page_token."""
    page_size = max(1, min(int(request.args.get("page_size", 30)), 300))
    next_page_token = request.args.get("next_page_token", "")
    participants = []
    num_participants = random.randint(1, page_size)
    
    for _ in range(num_participants):
        participant = {
            "id": generate_random_string(22),
            "participant_id": str(random.randint(10000000, 99999999)),
            "user_name": f"User_{generate_random_string(8)}",
            "email": f"user_{generate_random_string(8)}@example.com",
            "qos": generate_qos_data()
        }
        participants.append(participant)

    response = {
        "page_size": page_size,
        "next_page_token": generate_random_string(32) if num_participants == page_size else "",
        "participants": participants
    }

    return jsonify(response)

@qss_bp.route("/metrics/webinars/<webinar_id>/participants/qos_summary", methods=["GET"])
@require_auth
def get_webinar_participants_qos(webinar_id):
    """Query: page_size, next_page_token."""
    page_size = max(1, min(int(request.args.get("page_size", 30)), 300))
    next_page_token = request.args.get("next_page_token", "")

    participants = []
    num_participants = random.randint(1, page_size)
    
    for _ in range(num_participants):
        participant = {
            "id": generate_random_string(22),
            "participant_id": str(random.randint(10000000, 99999999)),
            "user_name": f"User_{generate_random_string(8)}",
            "email": f"user_{generate_random_string(8)}@example.com",
            "qos": generate_qos_data()
        }
        participants.append(participant)

    response = {
        "page_size": page_size,
        "next_page_token": generate_random_string(32) if num_participants == page_size else "",
        "participants": participants
    }

    return jsonify(response)

@qss_bp.route("/videosdk/sessions/<session_id>/users/qos_summary", methods=["GET"])
@require_auth
def get_session_users_qos(session_id):
    """Query: page_size, next_page_token."""
    page_size = max(1, min(int(request.args.get("page_size", 30)), 300))
    next_page_token = request.args.get("next_page_token", "")

    users = []
    num_users = random.randint(1, page_size)
    
    for _ in range(num_users):
        user = {
            "id": generate_random_string(22),
            "name": f"User_{generate_random_string(8)}",
            "user_key": generate_random_string(random.randint(10, 36)),
            "qos": generate_qos_data()
        }
        users.append(user)

    response = {
        "page_size": page_size,
        "next_page_token": generate_random_string(32) if num_users == page_size else "",
        "users": users
    }

    return jsonify(response) 