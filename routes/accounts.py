from flask import Blueprint, jsonify, request

accounts_bp = Blueprint('accounts', __name__)

@accounts_bp.route('/<accountId>/lock_settings', methods=['GET'])
def get_account_lock_settings(accountId):
    """Get an account's locked settings.
    
    Returns locked settings for the specified account as long as a valid access token is provided.
    """
    # Get authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "No authorization token provided"}), 401
        
    # Return a basic response since we just need to validate the token
    return jsonify({
        "schedule_meeting": {
            "host_video": False,
            "participant_video": False,
            "audio_type": True
        },
        "in_meeting": {
            "chat": True,
            "screen_sharing": True
        },
        "email_notification": {
            "cloud_recording_available_reminder": True
        },
        "recording": {
            "cloud_recording": True,
            "auto_recording": True
        }
    }) 