from flask import Blueprint, jsonify, request
from models.auth import require_auth
from helpers import generate_random_string
import time

mail_bp = Blueprint("mail", __name__, url_prefix="/emails")

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

@mail_bp.route("/mailboxes/<email>/drafts", methods=["GET"])
@require_auth
def list_drafts(email):
    """List drafts. Query: maxResults, pageToken."""
    max_results = min(int(request.args.get("maxResults", 100)), 500)
    page_token = request.args.get("pageToken", "")
    out = dict(MOCK_DRAFTS)
    out["resultSizeEstimate"] = min(len(out.get("drafts", [])), max_results)
    return jsonify(out)


@mail_bp.route("/mailboxes/<email>/labels", methods=["GET"])
@require_auth
def list_labels(email):
    """Query: maxResults, pageToken."""
    return jsonify(MOCK_LABELS)


@mail_bp.route("/mailboxes/<email>/threads", methods=["GET"])
@require_auth
def list_threads(email):
    """Query: maxResults, pageToken, q (search)."""
    max_results = min(int(request.args.get("maxResults", 100)), 500)
    q = request.args.get("q", "")
    out = dict(MOCK_THREADS)
    out["resultSizeEstimate"] = min(len(out.get("threads", [])), max_results)
    return jsonify(out)

@mail_bp.route("/mailboxes/<email>/messages/send", methods=["POST"])
@require_auth
def send_email(email):
    """Send email. Body: raw (base64, required), sendTime (optional), to, subject, etc."""
    try:
        data = request.get_json() or {}
        if not data.get("raw"):
            return jsonify({"error": {"code": "400", "message": "Validation failed", "details": "raw (base64 message) is required"}}), 400

        # Generate a mock message ID and thread ID
        message_id = f"{generate_random_string(16)}_e{int(time.time())}_{generate_random_string(3)}"
        
        # Prepare response
        response = {
            "id": message_id,
            "threadId": message_id,
            "labelIds": ["SCHEDULED"] if data.get("sendTime") else ["SENT"],
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": {"code": "500", "message": "Server error", "details": str(e)}}), 500