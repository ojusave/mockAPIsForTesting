from flask import Blueprint, jsonify, request
from models.auth import require_auth
from cache_config import cache
import time

chat_bp = Blueprint("chat", __name__)

# Store chat channels and messages in memory (replace with database in production)
channels = {}
messages = {}

def _get_mock_user_id():
    """Mock user ID for chat; in real Zoom API this comes from token."""
    return getattr(request, "user", None) and request.user.get("id") or "mock_user_id"


@chat_bp.route("/channels", methods=["GET"])
@require_auth
def list_channels():
    """List user's chat channels"""
    return jsonify({
        "channels": list(channels.values()),
        "page_size": len(channels),
        "total_records": len(channels),
    })

@chat_bp.route("/channels", methods=["POST"])
@require_auth
def create_channel():
    """Create channel. Body: name (required), type (1=private, 2=private_with_owner, 3=public, 4=instant), channel_settings."""
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": {"code": "400", "message": "Validation failed", "details": "name is required"}}), 400
    channel_id = str(len(channels) + 1)
    new_channel = {
        "id": channel_id,
        "name": data["name"],
        "type": data.get("type", 1),
        "channel_settings": data.get("channel_settings") or {},
    }
    channels[channel_id] = new_channel
    return jsonify(new_channel), 201

@chat_bp.route("/channels/<channel_id>/messages", methods=["GET"])
@require_auth
def get_messages(channel_id):
    """List messages. Query: page_size, next_page_token, to_contact (optional)."""
    if channel_id not in channels:
        return jsonify({"error": {"code": "404", "message": "Channel not found"}}), 404
    page_size = min(int(request.args.get("page_size", 50)), 200)
    next_page_token = request.args.get("next_page_token", "")
    channel_messages = messages.get(channel_id, [])
    total = len(channel_messages)
    start = 0
    if next_page_token:
        try:
            start = int(next_page_token)
        except ValueError:
            pass
    page_msgs = channel_messages[start : start + page_size]
    return jsonify({
        "messages": page_msgs,
        "page_size": len(page_msgs),
        "next_page_token": str(start + page_size) if start + page_size < total else "",
    })

@chat_bp.route("/channels/<channel_id>/messages", methods=["POST"])
@require_auth
def send_message(channel_id):
    """Send message. Body: message (required), to_contact (optional)."""
    if channel_id not in channels:
        return jsonify({"error": {"code": "404", "message": "Channel not found"}}), 404
    data = request.get_json() or {}
    if not data.get("message") and not data.get("content"):
        return jsonify({"error": {"code": "400", "message": "Validation failed", "details": "message or content is required"}}), 400
    message = {
        "id": str(len(messages.get(channel_id, [])) + 1),
        "message": data.get("message") or data.get("content", ""),
        "sender": _get_mock_user_id(),
        "timestamp": int(time.time() * 1000),
    }
    
    if channel_id not in messages:
        messages[channel_id] = []
    messages[channel_id].append(message)
    
    return jsonify(message), 201

@chat_bp.route('/channels/<channel_id>/members', methods=['GET'])
@require_auth
def list_members(channel_id):
    """List members in a channel"""
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
        
    # In production, fetch members from database/Zoom API
    return jsonify({
        "members": [],
        "page_size": 0,
        "total_records": 0
    })

@chat_bp.route('/channels/<channel_id>/members', methods=['POST'])
@require_auth
def add_members(channel_id):
    """Add members to a channel"""
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
        
    data = request.get_json()
    # In production, add members to database/Zoom API
    
    return jsonify({
        "added_at": int(time.time() * 1000),
        "ids": []
    }), 201

@chat_bp.route('/channels/<channel_id>', methods=['GET'])
@require_auth
def get_channel(channel_id):
    """Get a specific channel"""
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
    
    return jsonify(channels[channel_id])

@chat_bp.route('/channels/<channel_id>', methods=['PATCH'])
@require_auth
def update_channel(channel_id):
    """Update a channel's settings"""
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
        
    data = request.get_json()
    channel = channels[channel_id]
    
    if "name" in data:
        channel["name"] = data["name"]
    if "channel_settings" in data:
        channel["channel_settings"].update(data["channel_settings"])
        
    return '', 204

@chat_bp.route('/channels/<channel_id>', methods=['DELETE'])
@require_auth
def delete_channel(channel_id):
    """Delete a channel"""
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
        
    channels.pop(channel_id)
    if channel_id in messages:
        messages.pop(channel_id)
        
    return '', 204

@chat_bp.route('/channels/<channel_id>/members/<member_id>', methods=['DELETE'])
@require_auth
def remove_member(channel_id, member_id):
    """Remove a member from a channel"""
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
        
    # In production, remove member from database/Zoom API
    return '', 204

@chat_bp.route('/channels/search', methods=['POST'])
@require_auth
def search_channels():
    """Search for channels"""
    data = request.get_json()
    needle = data.get('needle', '')
    
    # Simple search implementation
    found_channels = [
        channel for channel in channels.values()
        if needle.lower() in channel['name'].lower()
    ]
    
    return jsonify({
        "channels": found_channels,
        "page_size": len(found_channels),
        "total_records": len(found_channels)
    })

@chat_bp.route('/channels/<channel_id>/members/me', methods=['POST'])
@require_auth
def join_channel(channel_id):
    """Join a channel"""
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
        
    # In production, add current user to channel in database/Zoom API
    return jsonify({
        "added_at": int(time.time() * 1000),
        "id": _get_mock_user_id(),
        "member_id": f"member_{_get_mock_user_id()}",
    }), 201

@chat_bp.route('/channels/<channel_id>/members/me', methods=['DELETE'])
@require_auth
def leave_channel(channel_id):
    """Leave a channel"""
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
        
    # In production, remove current user from channel in database/Zoom API
    return '', 204

@chat_bp.route('/chat/users/<user_id>/messages', methods=['GET'])
@require_auth
@cache.memoize(timeout=3600)
def list_user_messages(user_id):
    """List messages for a specific user"""
    # In production, fetch from database/Zoom API
    user_messages = []
    for channel_msgs in messages.values():
        user_messages.extend([
            msg for msg in channel_msgs 
            if msg['sender'] == user_id
        ])
    
    return jsonify({
        "messages": user_messages,
        "page_size": len(user_messages),
        "next_page_token": None
    })

@chat_bp.route("/chat/users/<user_id>/messages", methods=["POST"])
@require_auth
def send_user_message(user_id):
    """Send a direct message to a user"""
    data = request.get_json()
    message = {
        "id": f"msg_{int(time.time())}",
        "message": data.get("message"),
        "sender": _get_mock_user_id(),
        "receiver": user_id,
        "timestamp": int(time.time() * 1000),
    }
    
    if 'direct_messages' not in messages:
        messages['direct_messages'] = []
    messages['direct_messages'].append(message)
    
    # Cache the message
    cache_key = f'message:{message["id"]}'
    cache.set(cache_key, message, timeout=3600)
    
    # Invalidate the user's message list cache
    cache.delete_memoized(list_user_messages, user_id)
    
    return jsonify(message), 201

@chat_bp.route('/chat/users/<user_id>/messages/<message_id>', methods=['GET'])
@chat_bp.route('/chat/users/<user_id>/messages/<message_id>', methods=['PUT', 'PATCH'])
@chat_bp.route('/chat/users/<user_id>/messages/<message_id>', methods=['DELETE'])
@require_auth
def get_user_message(user_id, message_id):
    """Get a specific message"""
    # Search in all messages
    for channel_msgs in messages.values():
        for msg in channel_msgs:
            if msg['id'] == message_id and (
                msg.get('sender') == user_id or 
                msg.get('receiver') == user_id
            ):
                return jsonify(msg)
    
    return jsonify({"error": "Message not found"}), 404

@chat_bp.route("/chat/users/me/messages", methods=["GET"])
@require_auth
def list_my_messages():
    """List messages for the authenticated user"""
    return list_user_messages(_get_mock_user_id())

@chat_bp.route("/chat/users/me/messages/<message_id>", methods=["GET"])
@require_auth
def get_my_message(message_id):
    """Get a specific message for the authenticated user"""
    return get_user_message(_get_mock_user_id(), message_id)

@chat_bp.route("/chat/users/me/messages/<message_id>", methods=["PUT", "PATCH"])
@require_auth
def update_my_message(message_id):
    """Update authenticated user's message"""
    data = request.get_json() or {}
    for channel_msgs in messages.values():
        for msg in channel_msgs:
            if msg.get("id") == message_id and msg.get("sender") == _get_mock_user_id():
                msg.update({k: v for k, v in data.items() if k in ("message",)})
                return jsonify(msg)
    return jsonify({"error": {"code": "404", "message": "Message not found"}}), 404

@chat_bp.route("/chat/users/me/messages/<message_id>", methods=["DELETE"])
@require_auth
def delete_my_message(message_id):
    """Delete authenticated user's message"""
    for channel_msgs in messages.values():
        for i, msg in enumerate(channel_msgs):
            if msg.get("id") == message_id and msg.get("sender") == _get_mock_user_id():
                channel_msgs.pop(i)
                return "", 204
    if "direct_messages" in messages:
        for i, msg in enumerate(messages["direct_messages"]):
            if msg.get("id") == message_id and msg.get("sender") == _get_mock_user_id():
                messages["direct_messages"].pop(i)
                return "", 204
    return jsonify({"error": {"code": "404", "message": "Message not found"}}), 404 