from flask import Blueprint, jsonify, request
from helpers import generate_random_string, get_next_file_content
import datetime
import random

qss_bp = Blueprint('qss', __name__)

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

@qss_bp.route('/metrics/meetings/<meeting_id>/participants/qos_summary', methods=['GET'])
def get_meeting_participants_qos(meeting_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    page_size = int(request.args.get('page_size', 1))
    next_page_token = request.args.get('next_page_token', '')

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

@qss_bp.route('/metrics/webinars/<webinar_id>/participants/qos_summary', methods=['GET'])
def get_webinar_participants_qos(webinar_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    page_size = int(request.args.get('page_size', 1))
    next_page_token = request.args.get('next_page_token', '')

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

@qss_bp.route('/videosdk/sessions/<session_id>/users/qos_summary', methods=['GET'])
def get_session_users_qos(session_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    page_size = int(request.args.get('page_size', 1))
    next_page_token = request.args.get('next_page_token', '')

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