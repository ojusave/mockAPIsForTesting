from flask import Blueprint, jsonify, request
import time

mail_bp = Blueprint('mail', __name__, url_prefix='/emails')

# Mock data for mail responses
MOCK_DRAFTS = {
    "drafts": [
        {
            "id": "89f1000000000000_e856432f45a75bea_001",
            "message": {
                "id": "89f1000000000000_e856432f45a75bea_001",
                "threadId": "89f1000000000000_e856432f45a88bea_001"
            }
        }
    ],
    "nextPageToken": "e856432f45a75bea",
    "resultSizeEstimate": 1
}

MOCK_LABELS = {
    "labels": [
        {
            "id": "Label_1",
            "name": "MyVacation",
            "parentId": "Label_0",
            "labelLevel": 1,
            "messageListVisibility": "show",
            "labelListVisibility": "labelShow",
            "messagesTotal": 100,
            "messagesUnread": 98,
            "threadsTotal": 80,
            "threadsUnread": 78,
            "color": {
                "textColor": "#000000",
                "backgroundColor": "#cccccc"
            },
            "type": "user"
        }
    ]
}

MOCK_THREADS = {
    "threads": [
        {
            "id": "6ddf401500000000_e858101177b8152c_001",
            "snippet": "Based on previous discussion, we reached preliminary",
            "historyId": "1499070",
            "threadName": "The latest status of Project Prometheus",
            "status": "normal"
        }
    ],
    "nextPageToken": "e8562c0a6ba2b3cd",
    "resultSizeEstimate": 10
}

@mail_bp.route('/mailboxes/<email>/drafts', methods=['GET'])
def list_drafts(email):
    return jsonify(MOCK_DRAFTS)

@mail_bp.route('/mailboxes/<email>/labels', methods=['GET'])
def list_labels(email):
    return jsonify(MOCK_LABELS)

@mail_bp.route('/mailboxes/<email>/threads', methods=['GET'])
def list_threads(email):
    return jsonify(MOCK_THREADS)

@mail_bp.route('/mailboxes/<email>/messages/send', methods=['POST'])
def send_email(email):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('raw'):
            return jsonify({"error": "Missing required field: raw"}), 400

        # Generate a mock message ID and thread ID
        message_id = f"{generate_random_string(16)}_e{int(time.time())}_{generate_random_string(3)}"
        
        # Prepare response
        response = {
            "id": message_id,
            "threadId": message_id,  # Using same ID for thread in this mock
            "labelIds": ["SCHEDULED"] if data.get('sendTime') else ["SENT"]
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Add the generate_random_string function if not already present
def generate_random_string(length):
    """Generate a random string of specified length."""
    import random
    import string
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Add more mail-related routes as needed 