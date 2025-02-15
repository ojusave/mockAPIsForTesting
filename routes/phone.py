from flask import Blueprint, jsonify, request

phone_bp = Blueprint('phone', __name__)

# Mock data for phone responses
MOCK_PHONE_SETTINGS = {
    "call_live_transcription": {
        "enable": True,
        "locked": False,
        "locked_by": "account",
        "transcription_start_prompt": {
            "enable": True,
            "audio_id": "yCT14TwySDGVUypVlKNEyA",
            "audio_name": "example.mp3"
        }
    },
    "local_survivability_mode": {
        "enable": True,
        "locked": False,
        "locked_by": "account"
    }
}

MOCK_PHONE_NUMBERS = {
    "customize_numbers": [
        {
            "customize_id": "8_RkKw9OQ42oYsXqJJjs4A",
            "phone_number_id": "55JUZPwERHuGttd_j4qBsA",
            "phone_number": "+12055437350",
            "display_name": "test abc",
            "incoming": True,
            "outgoing": True
        }
    ],
    "next_page_token": "BJLYC6PABbAHdjwSkGVQeeR6B1juwHqj3G2",
    "page_size": 30,
    "total_records": 10
}

@phone_bp.before_request
def verify_token():
    # Add token verification logic here if needed
    pass

@phone_bp.route('/account_settings', methods=['GET'])
def get_account_settings():
    return jsonify(MOCK_PHONE_SETTINGS)

@phone_bp.route('/outbound_caller_id/customized_numbers', methods=['GET'])
def get_customized_numbers():
    return jsonify(MOCK_PHONE_NUMBERS)

@phone_bp.route('/outbound_caller_id/customized_numbers/<customize_id>', methods=['GET'])
def get_customized_number(customize_id):
    for number in MOCK_PHONE_NUMBERS['customize_numbers']:
        if number['customize_id'] == customize_id:
            return jsonify(number)
    return jsonify({"error": "Number not found"}), 404

@phone_bp.route('/outbound_caller_id/customized_numbers', methods=['POST'])
def add_customized_number():
    new_number = request.json
    MOCK_PHONE_NUMBERS['customize_numbers'].append(new_number)
    return jsonify(new_number), 201

@phone_bp.route('/outbound_caller_id/customized_numbers/<customize_id>', methods=['DELETE'])
def delete_customized_number(customize_id):
    global MOCK_PHONE_NUMBERS
    MOCK_PHONE_NUMBERS['customize_numbers'] = [
        number for number in MOCK_PHONE_NUMBERS['customize_numbers']
        if number['customize_id'] != customize_id
    ]
    return jsonify({"message": "Number deleted"}), 204

@phone_bp.route('/call_live_transcription', methods=['GET'])
def get_live_transcription_settings():
    return jsonify(MOCK_PHONE_SETTINGS['call_live_transcription'])

@phone_bp.route('/call_live_transcription', methods=['PATCH'])
def update_live_transcription_settings():
    settings = request.json
    MOCK_PHONE_SETTINGS['call_live_transcription'].update(settings)
    return jsonify(MOCK_PHONE_SETTINGS['call_live_transcription'])

@phone_bp.route('/local_survivability_mode', methods=['GET'])
def get_local_survivability_mode():
    return jsonify(MOCK_PHONE_SETTINGS['local_survivability_mode'])

@phone_bp.route('/local_survivability_mode', methods=['PATCH'])
def update_local_survivability_mode():
    settings = request.json
    MOCK_PHONE_SETTINGS['local_survivability_mode'].update(settings)
    return jsonify(MOCK_PHONE_SETTINGS['local_survivability_mode'])

# New endpoints based on OpenAPI specification
@phone_bp.route('/phone/account_settings', methods=['GET'])
def list_zoom_phone_account_settings():
    # Logic to list account settings
    return jsonify(MOCK_PHONE_SETTINGS), 200

@phone_bp.route('/phone/outbound_caller_id/customized_numbers', methods=['GET'])
def list_customize_outbound_caller_numbers():
    # Logic to list customized outbound caller ID numbers
    return jsonify({"customized_numbers": []}), 200

@phone_bp.route('/phone/outbound_caller_id/customized_numbers', methods=['POST'])
def add_outbound_caller_id():
    # Logic to add a customized outbound caller ID
    new_number = request.json
    MOCK_PHONE_NUMBERS['customize_numbers'].append(new_number)
    return jsonify(new_number), 201

@phone_bp.route('/phone/outbound_caller_id/customized_numbers/<customize_id>', methods=['DELETE'])
def delete_outbound_caller_id(customize_id):
    # Logic to delete a customized outbound caller ID
    global MOCK_PHONE_NUMBERS
    MOCK_PHONE_NUMBERS['customize_numbers'] = [
        number for number in MOCK_PHONE_NUMBERS['customize_numbers']
        if number['customize_id'] != customize_id
    ]
    return jsonify({"message": "Number deleted"}), 204

@phone_bp.route('/phone/alert_settings', methods=['GET'])
def get_alert_settings():
    # Logic to retrieve alert settings
    return jsonify({"alert_settings": []})  # Placeholder for alert settings

@phone_bp.route('/phone/voice_mails', methods=['GET'])
def get_voicemails():
    # Logic to retrieve voicemails
    return jsonify({"voicemails": []})  # Placeholder for voicemails

@phone_bp.route('/phone/rooms', methods=['GET'])
def list_zoom_rooms():
    # Logic to list Zoom Rooms
    return jsonify({"rooms": []}), 200

@phone_bp.route('/phone/rooms/<room_id>', methods=['GET'])
def get_zoom_room(room_id):
    # Logic to get a specific Zoom Room
    return jsonify({"room": {}}), 200

@phone_bp.route('/phone/rooms', methods=['POST'])
def add_zoom_room():
    # Logic to add a Zoom Room
    new_room = request.json
    return jsonify(new_room), 201

@phone_bp.route('/phone/rooms/<room_id>', methods=['DELETE'])
def delete_zoom_room(room_id):
    # Logic to delete a Zoom Room
    return jsonify({"message": "Room deleted"}), 204

@phone_bp.route('/phone/rooms/<room_id>/calling_plans', methods=['POST'])
def assign_calling_plan_to_room(room_id):
    # Logic to assign calling plans to a Zoom Room
    return jsonify({"message": "Calling plan assigned"}), 201

@phone_bp.route('/phone/rooms/<room_id>/calling_plans/<type>', methods=['DELETE'])
def unassign_calling_plan_from_room(room_id, type):
    # Logic to unassign a calling plan from a Zoom Room
    return jsonify({"message": "Calling plan removed"}), 204

@phone_bp.route('/phone/rooms/<room_id>/phone_numbers', methods=['POST'])
def assign_phone_number_to_zoom_room(room_id):
    # Logic to assign phone numbers to a Zoom Room
    return jsonify({"message": "Phone number assigned"}), 201

@phone_bp.route('/phone/rooms/<room_id>/phone_numbers/<phone_number_id>', methods=['DELETE'])
def unassign_phone_number_from_zoom_room(room_id, phone_number_id):
    # Logic to unassign a phone number from a Zoom Room
    return jsonify({"message": "Phone number removed"}), 204

# Additional endpoints can be added similarly based on the OpenAPI specification

# Add more phone-related routes as needed 