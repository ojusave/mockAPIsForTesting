from flask import Blueprint, jsonify, request
from helpers import generate_random_string, BASE_URL, get_next_file_content
import datetime
import uuid
import random
import os
import json

meetings_bp = Blueprint('meetings', __name__)

FILES_DIR = 'files'

def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + datetime.timedelta(days=random_number_of_days)

def get_random_file_content():
    file_content, _ = get_next_file_content()
    return file_content

def generate_meeting_data(user_id, from_date, to_date):
    num_meetings = random.randint(1, 10)
    meetings = []
    for _ in range(num_meetings):
        file_content = get_random_file_content()
        summary = file_content.get('summary', {})
        
        meeting_id = generate_random_string(22)
        start_time = generate_random_date(from_date, to_date)
        duration = random.randint(30, 120)
        meetings.append({
            "uuid": generate_random_string(22),
            "id": meeting_id,
            "host_id": user_id,
            "topic": summary.get('summary_title', f"Meeting about {generate_random_string(5)}"),
            "type": 2,
            "start_time": start_time.isoformat() + "Z",
            "duration": duration,
            "timezone": random.choice(["America/Los_Angeles", "America/New_York", "Asia/Tokyo", "Europe/London"]),
            "created_at": start_time.isoformat() + "Z",
            "join_url": f"{BASE_URL}/j/{meeting_id}"
        })
    return meetings

@meetings_bp.route('/users/<user_id>/meetings', methods=['GET'])
def get_meetings(user_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    from_date = request.args.get('from', '2024-07-20')
    to_date = request.args.get('to', '2024-08-18')

    try:
        from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d')
        to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    meetings = generate_meeting_data(user_id, from_date_obj, to_date_obj)

    response_data = {
        "page_size": 30,
        "total_records": len(meetings),
        "next_page_token": "",
        "meetings": meetings
    }

    return jsonify(response_data)

@meetings_bp.route('/meetings/<meeting_id>/meeting_summary', methods=['GET'])
def get_meeting_summary(meeting_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    try:
        file_content = get_random_file_content()
        summary = file_content.get('summary', {})
        
        if not summary:
            return jsonify({"error": "Summary not found"}), 404

        meeting_duration = random.randint(30, 120)  # Random duration between 30 and 120 minutes
        current_time = datetime.datetime.now()
        start_time = current_time - datetime.timedelta(minutes=meeting_duration)
        
        meeting_summary = {
            "meeting_host_id": str(uuid.uuid4()),
            "meeting_host_email": f"{generate_random_string(6)}@example.com",
            "meeting_uuid": generate_random_string(22),
            "meeting_id": meeting_id,
            "meeting_topic": summary.get('summary_title', 'Untitled Meeting'),
            "meeting_start_time": start_time.isoformat() + "Z",
            "meeting_end_time": current_time.isoformat() + "Z",
            "summary_start_time": current_time.isoformat() + "Z",
            "summary_end_time": (current_time + datetime.timedelta(minutes=5)).isoformat() + "Z",
            "summary_created_time": current_time.isoformat() + "Z",
            "summary_last_modified_time": current_time.isoformat() + "Z",
            "summary_title": summary.get('summary_title', 'Meeting Summary'),
            "summary_overview": summary.get('summary_overview', ''),
            "summary_details": [
                {
                    "label": "Meeting overview",
                    "summary": summary.get('summary_overview', '')
                }
            ] + [{"label": f"Point {i+1}", "summary": detail} for i, detail in enumerate(summary.get('summary_details', []))],
            "next_steps": summary.get('next_steps', []),
            "edited_summary": {
                "summary_details": summary.get('summary_overview', ''),
                "next_steps": summary.get('next_steps', [])
            }
        }

        return jsonify(meeting_summary)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# New route to handle VTT file download
@meetings_bp.route('/rec/download/<path:path>', methods=['GET'])
def download_vtt(path):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    try:
        file_content = get_random_file_content()
        vtt_data = file_content.get('vtt_data', '')
        
        if not vtt_data:
            return jsonify({"error": "VTT data not found"}), 404

        return vtt_data, 200, {'Content-Type': 'text/vtt'}

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500