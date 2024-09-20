from flask import Blueprint, jsonify, request
from helpers import generate_random_string, fetch_stored_summary, get_random_pre_generated_content, BASE_URL
import datetime
import uuid
import random

meetings_bp = Blueprint('meetings', __name__)

def generate_meeting_data(user_id, from_date, to_date):
    num_meetings = random.randint(1, 10)
    meetings = []
    for _ in range(num_meetings):
        pre_generated = get_random_pre_generated_content()
        if pre_generated:
            meeting_id = pre_generated['meeting_id']
            meeting_topic = pre_generated.get('meeting_topic', f"Meeting about {generate_random_string(5)}")
            start_time = generate_random_date(from_date, to_date)
            duration = random.randint(30, 120)
            meetings.append({
                "uuid": generate_random_string(22),
                "id": meeting_id,
                "host_id": user_id,
                "topic": meeting_topic,
                "type": 2,
                "start_time": start_time.isoformat() + "Z",
                "duration": duration,
                "timezone": random.choice(["America/Los_Angeles", "America/New_York", "Asia/Tokyo", "Europe"]),
                "created_at": start_time.isoformat() + "Z",
                "join_url": f"{BASE_URL}/j/{meeting_id}"
            })
    return meetings

def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + datetime.timedelta(days=random_number_of_days)

@meetings_bp.route('/users/meetings', methods=['GET'])
def get_meetings():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "No user_id provided"}), 400

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

    max_retries = 3
    retry_delay = 10  # seconds

    for attempt in range(max_retries):
        summary = fetch_stored_summary(meeting_id)
        
        if not summary:
            return jsonify({"error": "Summary not found"}), 404

        meeting_topic = summary.get('meeting_topic', f"Meeting about {generate_random_string(5)}")
        summary_content = summary.get('summary', '')

        # Check for error messages
        if "Error generating summary for meeting" in summary_content or "Error generating VTT for meeting" in summary_content:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                return jsonify({"error": "Failed to generate summary after multiple attempts"}), 500

        # Parse the summary content to extract next steps
        next_steps = []
        if "Next Steps" in summary_content:
            next_steps_section = summary_content.split("Next Steps")[-1].strip()
            next_steps = [step.strip() for step in next_steps_section.split('\n') if step.strip()]

        # Extract the summary overview (everything before "Next Steps")
        summary_overview = summary_content.split("Next Steps")[0].strip()

        meeting_duration = 103  # Example duration in minutes
        current_time = datetime.datetime.now()
        
        meeting_summary = {
            "meeting_host_id": str(uuid.uuid4()),
            "meeting_host_email": f"{generate_random_string(6)}@example.com",
            "meeting_uuid": generate_random_string(22),
            "meeting_id": meeting_id,
            "meeting_topic": meeting_topic,
            "meeting_start_time": (current_time - datetime.timedelta(minutes=meeting_duration)).isoformat() + "Z",
            "meeting_end_time": current_time.isoformat() + "Z",
            "summary_start_time": current_time.isoformat() + "Z",
            "summary_end_time": current_time.isoformat() + "Z",
            "summary_created_time": current_time.isoformat() + "Z",
            "summary_last_modified_time": current_time.isoformat() + "Z",
            "summary_title": f"Meeting summary for {meeting_topic}",
            "summary_overview": summary_overview,
            "summary_details": [
                {
                    "label": "Meeting overview",
                    "summary": summary_overview
                }
            ],
            "next_steps": next_steps,
            "edited_summary": {
                "summary_details": summary_overview,
                "next_steps": next_steps
            }
        }

        return jsonify(meeting_summary)

    # If we've exhausted all retries
    return jsonify({"error": "Failed to generate summary after multiple attempts"}), 500