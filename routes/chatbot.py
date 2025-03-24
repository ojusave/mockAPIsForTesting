from flask import Blueprint, jsonify, request
import time
from helpers import generate_random_string

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/im/chat')

@chatbot_bp.route('/messages', methods=['POST'])
def send_chat_message():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    try:
        data = request.get_json()
        
        # Generate mock response with default values if fields are missing
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        response = {
            "message_id": generate_random_string(24),  # Mock message ID
            "robot_jid": data.get('robot_jid', 'default_robot@xmpp.zoom.us'),
            "sent_time": current_time,
            "to_jid": data.get('to_jid', 'default_user@xmpp.zoom.us')
        }

        return jsonify(response), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500 