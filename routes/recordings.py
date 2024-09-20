from flask import Blueprint, jsonify, request, Response
from helpers import BASE_URL, get_next_file_content, generate_random_string, generate_random_date
import random
import datetime
import uuid
import logging

recordings_bp = Blueprint('recordings', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_recordings_data(user_id=None, meeting_id=None, start_date=None, end_date=None):
    num_recordings = random.randint(1, 5)
    recordings = []

    for _ in range(num_recordings):
        file_content, _ = get_next_file_content()
        current_meeting_id = meeting_id or generate_random_string(22)
        current_user_id = user_id or generate_random_string(22)
        
        start_time = generate_random_date(start_date, end_date)
        meeting_topic = file_content.get('summary', {}).get('summary_title', f"Meeting about {generate_random_string(5)}")
        meeting_duration = random.randint(30, 200)

        vtt_content = file_content.get('vtt_data', "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nThis is a sample VTT content.")
        vtt_file_size = len(vtt_content)

        recording_files = [{
            "id": str(uuid.uuid4()),
            "meeting_id": current_meeting_id,
            "recording_start": start_time.isoformat() + "Z",
            "recording_end": (start_time + datetime.timedelta(minutes=meeting_duration)).isoformat() + "Z",
            "file_type": "TRANSCRIPT",
            "file_extension": "VTT",
            "file_size": vtt_file_size,
            "play_url": f"{BASE_URL}/rec/play/{generate_random_string(10)}",
            "download_url": f"{BASE_URL}/rec/download/{current_meeting_id}/transcript.vtt",
            "status": "completed",
            "recording_type": "shared_screen_with_speaker_view"
        }]

        # Add other random file types
        other_file_types = ["MP4", "M4A", "JSON"]
        for file_type in other_file_types:
            recording_files.append({
                "id": str(uuid.uuid4()),
                "meeting_id": current_meeting_id,
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
            "uuid": current_meeting_id,
            "id": current_meeting_id,
            "host_id": current_user_id,
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
    token = request.headers.get('Authorization')
    if not token:
        logger.warning("No authorization token provided")
        return jsonify({"error": "No token provided"}), 401
    
    from_date = request.args.get('from', '2024-08-20')
    to_date = request.args.get('to', '2024-09-19')
    page_size = int(request.args.get('page_size', 300))

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
            "page_size": page_size,
            "total_records": len(recordings),
            "page_count": max(1, len(recordings) // page_size + (1 if len(recordings) % page_size > 0 else 0)),
            "next_page_token": "",
            "meetings": recordings
        }

        logger.info(f"Successfully generated recordings data. User ID: {user_id}")
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"An error occurred while generating recordings data: {str(e)}", exc_info=True)
        return jsonify({"error": "An internal server error occurred"}), 500

@recordings_bp.route('/rec/download/<path:path>', methods=['GET'])
def download_vtt(path):
    logger.info(f"Attempting to download VTT file: {path}")
    
    try:
        file_content, _ = get_next_file_content()
        vtt_data = file_content.get('vtt_data', '')
        
        if not vtt_data:
            logger.warning(f"VTT data not found for path: {path}")
            return jsonify({"error": "VTT data not found"}), 404

        logger.info(f"Successfully retrieved VTT data for path: {path}")
        logger.debug(f"VTT data preview: {vtt_data[:100]}...")  # Log first 100 characters
        
        return Response(vtt_data, mimetype='text/vtt')

    except Exception as e:
        logger.error(f"An error occurred while downloading VTT file: {str(e)}", exc_info=True)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
