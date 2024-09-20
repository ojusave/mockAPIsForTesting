from flask import Blueprint, jsonify, request
import random
import string
import datetime
import uuid
import logging
from helpers import BASE_URL, fetch_stored_vtt, get_random_pre_generated_content

recordings_bp = Blueprint('recordings', __name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + datetime.timedelta(days=random_number_of_days)

def generate_recordings_data(user_id=None, meeting_id=None, start_date=None, end_date=None):
    num_recordings = random.randint(1, 5)
    recordings = []

    for _ in range(num_recordings):
        pre_generated = get_random_pre_generated_content()
        if pre_generated:
            meeting_id = pre_generated['meeting_id']
            start_time = generate_random_date(start_date, end_date)
            meeting_topic = pre_generated.get('meeting_topic', f"Meeting about {generate_random_string(5)}")
            meeting_duration = random.randint(30, 200)

            vtt_content = pre_generated['vtt_content']
            vtt_file_size = len(vtt_content)

            recording_files = [{
                "id": str(uuid.uuid4()),
                "meeting_id": meeting_id,
                "recording_start": start_time.isoformat() + "Z",
                "recording_end": (start_time + datetime.timedelta(minutes=meeting_duration)).isoformat() + "Z",
                "file_type": "TRANSCRIPT",
                "file_extension": "VTT",
                "file_size": vtt_file_size,
                "play_url": f"{BASE_URL}/rec/play/{generate_random_string(10)}",
                "download_url": f"{BASE_URL}/rec/download/{meeting_id}/transcript.vtt",
                "status": "completed",
                "recording_type": "shared_screen_with_speaker_view"
            }]

            # Add other random file types
            other_file_types = ["MP4", "M4A", "JSON"]
            for file_type in other_file_types:
                recording_files.append({
                    "id": str(uuid.uuid4()),
                    "meeting_id": meeting_id,
                    "recording_start": start_time.isoformat() + "Z",
                    "recording_end": (start_time + datetime.timedelta(minutes=meeting_duration)).isoformat() + "Z",
                    "file_type": file_type,
                    "file_extension": file_type,
                    "file_size": random.randint(1000000, 200000000),
                    "play_url": f"{BASE_URL}/rec/play/{generate_random_string(10)}",
                    "download_url": f"{BASE_URL}/rec/download/{generate_random_string(10)}",
                    "status": "completed",
                    "recording_type": random.choice(["shared_screen_with_speaker_view", "audio_only", "chat_file"])
                })

            recordings.append({
                "uuid": generate_random_string(22),
                "id": meeting_id,
                "host_id": user_id,
                "topic": meeting_topic,
                "start_time": start_time.isoformat() + "Z",
                "duration": meeting_duration,
                "total_size": sum(file['file_size'] for file in recording_files),
                "recording_count": len(recording_files),
                "recording_files": recording_files
            })

    return recordings

@recordings_bp.route('/users/<user_id>/recordings', methods=['GET'])
def get_user_recordings(user_id):
    logger.info(f"Received request for user recordings. User ID: {user_id}")
    
    token = request.headers.get('Authorization')
    if not token:
        logger.warning("No authorization token provided")
        return jsonify({"error": "No token provided"}), 401

    from_date = request.args.get('from', '2024-08-20')
    to_date = request.args.get('to', '2024-09-19')

    logger.debug(f"Date range: from {from_date} to {to_date}")

    try:
        from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d')
        to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d')
    except ValueError as e:
        logger.error(f"Invalid date format: {str(e)}")
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    try:
        recordings = generate_recordings_data(user_id=user_id, start_date=from_date_obj, end_date=to_date_obj)

        response_data = {
            "from": from_date,
            "to": to_date,
            "page_size": 30,
            "total_records": len(recordings),
            "page_count": len(recordings) // 30 + 1,
            "next_page_token": "",
            "meetings": recordings
        }

        logger.info(f"Successfully generated recordings data for user {user_id}")
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"An error occurred while generating recordings data: {str(e)}", exc_info=True)
        return jsonify({"error": "An internal server error occurred"}), 500