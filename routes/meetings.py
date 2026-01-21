from flask import Blueprint, jsonify, request
from helpers import generate_random_string, BASE_URL, get_next_file_content
import datetime
import uuid
import random
import os
import json
from cache_config import cache
from functools import wraps
from models.auth import require_auth

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
@require_auth
@cache.memoize(timeout=3600)
def get_meetings(user_id):

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

def get_cached_meeting_base_data(meeting_id):
    """Get or create consistent base meeting data for a meeting ID"""
    cache_key = f'meeting_base_data_{meeting_id}'
    
    # Try to get from cache first
    base_data = cache.get(cache_key)
    if base_data is not None:
        return base_data
        
    # If not in cache, generate new data
    file_content = get_random_file_content()
    summary = file_content.get('summary', {})
    
    base_data = {
        'topic': summary.get('summary_title', f"Meeting about {generate_random_string(5)}"),
        'summary': summary,
        'file_content': file_content
    }
    
    # Cache for 1 hour
    cache.set(cache_key, base_data, timeout=3600)
    return base_data

@meetings_bp.route('/users/<user_id>/meetings/<meeting_id>', methods=['GET'])
@require_auth
@cache.memoize(timeout=3600)
def get_meeting(user_id, meeting_id):

    try:
        # Get consistent base data
        base_data = get_cached_meeting_base_data(meeting_id)
        
        current_time = datetime.datetime.now()
        duration = random.randint(30, 120)
        
        meeting_data = {
            "uuid": meeting_id,
            "id": meeting_id,
            "host_id": user_id,
            "host_email": f"{generate_random_string(6)}@example.com",
            "topic": base_data['topic'],  # Use consistent topic
            "type": 2,
            "start_time": current_time.isoformat() + "Z",
            "duration": duration,
            "timezone": random.choice(["America/Los_Angeles", "America/New_York", "Asia/Tokyo", "Europe/London"]),
            "created_at": (current_time - datetime.timedelta(days=1)).isoformat() + "Z",
            "join_url": f"{BASE_URL}/j/{meeting_id}",
            "start_url": f"{BASE_URL}/s/{meeting_id}",
            "password": generate_random_string(6),
            "settings": {
                "host_video": True,
                "participant_video": False,
                "join_before_host": False,
                "mute_upon_entry": True,
                "waiting_room": True,
                "meeting_authentication": False
            }
        }

        return jsonify(meeting_data)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@meetings_bp.route('/meetings/<meeting_id>/meeting_summary', methods=['GET'])
@require_auth
@cache.memoize(timeout=3600)
def get_meeting_summary(meeting_id):

    try:
        # Get consistent base data
        base_data = get_cached_meeting_base_data(meeting_id)
        summary = base_data['summary']
        
        if not summary:
            return jsonify({"error": "Summary not found"}), 404

        meeting_duration = random.randint(30, 120)
        current_time = datetime.datetime.now()
        start_time = current_time - datetime.timedelta(minutes=meeting_duration)
        
        meeting_summary = {
            "meeting_host_id": str(uuid.uuid4()),
            "meeting_host_email": f"{generate_random_string(6)}@example.com",
            "meeting_uuid": meeting_id,  # Use consistent meeting ID
            "meeting_id": meeting_id,
            "meeting_topic": base_data['topic'],  # Use consistent topic
            "meeting_start_time": start_time.isoformat() + "Z",
            "meeting_end_time": current_time.isoformat() + "Z",
            "summary_start_time": current_time.isoformat() + "Z",
            "summary_end_time": (current_time + datetime.timedelta(minutes=5)).isoformat() + "Z",
            "summary_created_time": current_time.isoformat() + "Z",
            "summary_last_modified_time": current_time.isoformat() + "Z",
            "summary_title": base_data['topic'],  # Use consistent topic
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
@require_auth
def download_vtt(path):

    try:
        file_content = get_random_file_content()
        vtt_data = file_content.get('vtt_data', '')
        
        if not vtt_data:
            return jsonify({"error": "VTT data not found"}), 404

        return vtt_data, 200, {'Content-Type': 'text/vtt'}

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@meetings_bp.route('/past_meetings/<meeting_id>/participants', methods=['GET'])
@require_auth
def get_past_meeting_participants(meeting_id):

    try:
        # Get pagination parameters from query string
        page_size = min(int(request.args.get('page_size', 30)), 300)  # Max 300 per API spec
        next_page_token = request.args.get('next_page_token', '')

        # Generate random number of participants (1-10 for testing)
        num_participants = random.randint(1, 10)
        
        # Generate mock participants data
        participants = []
        current_time = datetime.datetime.now()
        
        for _ in range(num_participants):
            join_time = current_time - datetime.timedelta(minutes=random.randint(30, 120))
            leave_time = join_time + datetime.timedelta(minutes=random.randint(5, 60))
            duration = int((leave_time - join_time).total_seconds())
            
            participant = {
                "id": generate_random_string(22),
                "name": f"User {generate_random_string(5)}",
                "user_id": str(random.randint(10000000, 99999999)),
                "registrant_id": generate_random_string(22),
                "user_email": f"{generate_random_string(6)}@example.com",
                "join_time": join_time.isoformat() + "Z",
                "leave_time": leave_time.isoformat() + "Z",
                "duration": duration,
                "failover": False,
                "status": random.choice(["in_meeting", "in_waiting_room"]),
                "internal_user": random.choice([True, False])
            }
            participants.append(participant)

        response_data = {
            "next_page_token": generate_random_string(32) if num_participants >= page_size else "",
            "page_count": 1,
            "page_size": page_size,
            "total_records": num_participants,
            "participants": participants
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@meetings_bp.route('/users/<user_id>/meetings/<meeting_id>', methods=['PATCH'])
@require_auth
def update_meeting(user_id, meeting_id):
    # After updating meeting
    cache.delete_memoized(get_meeting, user_id, meeting_id)
    # ... rest of the code

@meetings_bp.route('/users/<user_id>/meetings/<meeting_id>', methods=['DELETE'])
@require_auth
def delete_meeting(user_id, meeting_id):
    cache.delete_memoized(get_meeting, user_id, meeting_id)
    cache.delete_memoized(get_meeting_summary, meeting_id)
    cache.delete(f'meeting_base_data_{meeting_id}')
    return '', 204