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
        
        # Validate required fields
        required_fields = ['robot_jid', 'to_jid', 'content']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Generate mock response
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        response = {
            "message_id": generate_random_string(24),  # Mock message ID
            "robot_jid": data['robot_jid'],
            "sent_time": current_time,
            "to_jid": data['to_jid']
        }

        return jsonify(response), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500 