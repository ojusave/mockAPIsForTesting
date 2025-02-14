from flask import Blueprint, jsonify

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

# Add more phone-related routes as needed 