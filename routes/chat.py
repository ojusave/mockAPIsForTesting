from flask import Blueprint, jsonify, request
from functools import wraps
import time

chat_bp = Blueprint('chat', __name__)

# Simple auth decorator that just checks for bearer token presence
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "No valid bearer token provided"}), 401
            
        # Add a mock user to the request
        request.user = {"id": "mock_user_id"}
        return f(*args, **kwargs)
    return decorated

# Store chat channels and messages in memory (replace with database in production)
channels = {}
messages = {}

@chat_bp.route('/channels', methods=['GET'])
@require_auth
def list_channels():
    """List user's chat channels"""
    # In production, fetch channels from database/Zoom API
    return jsonify({
        "channels": [channel for channel in channels.values()],
        "page_size": len(channels),
        "total_records": len(channels)
    })

@chat_bp.route('/channels', methods=['POST']) 
@require_auth
def create_channel():
    """Create a new chat channel"""
    data = request.get_json()
    
    channel_id = str(len(channels) + 1)  # Simple ID generation
    new_channel = {
        "id": channel_id,
        "name": data.get("name"),
        "type": data.get("type", 1),
        "channel_settings": data.get("channel_settings", {})
    }
    
    channels[channel_id] = new_channel
    
    return jsonify(new_channel), 201

@chat_bp.route('/channels/<channel_id>/messages', methods=['GET'])
@require_auth
def get_messages(channel_id):
    """Get messages for a channel"""
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
        
    channel_messages = messages.get(channel_id, [])
    return jsonify({
        "messages": channel_messages,
        "page_size": len(channel_messages)
    })

@chat_bp.route('/channels/<channel_id>/messages', methods=['POST'])
@require_auth
def send_message(channel_id):
    """Send a message to a channel"""
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
        
    data = request.get_json()
    message = {
        "id": str(len(messages.get(channel_id, [])) + 1),
        "message": data.get("message"),
        "sender": request.user.get("id"),  # From auth middleware
        "timestamp": int(time.time() * 1000)
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
        "id": request.user.get("id"),
        "member_id": f"member_{request.user.get('id')}"
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

@chat_bp.route('/chat/users/<user_id>/messages', methods=['POST'])
@require_auth
def send_user_message(user_id):
    """Send a direct message to a user"""
    data = request.get_json()
    
    message = {
        "id": f"msg_{int(time.time())}",
        "message": data.get("message"),
        "sender": request.user.get("id"),
        "receiver": user_id,
        "timestamp": int(time.time() * 1000)
    }
    
    # In production, save to database/send via Zoom API
    if 'direct_messages' not in messages:
        messages['direct_messages'] = []
    messages['direct_messages'].append(message)
    
    return jsonify(message), 201

@chat_bp.route('/chat/users/<user_id>/messages/<message_id>', methods=['GET'])
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

@chat_bp.route('/chat/users/<user_id>/messages/<message_id>', methods=['PUT', 'PATCH'])
@require_auth
def update_user_message(user_id, message_id):
    """Update a message"""
    data = request.get_json()
    
    # Search and update message
    for channel_msgs in messages.values():
        for msg in channel_msgs:
            if msg['id'] == message_id and msg['sender'] == user_id:
                msg['message'] = data.get('message', msg['message'])
                msg['updated_at'] = int(time.time() * 1000)
                return '', 204
    
    return jsonify({"error": "Message not found or unauthorized"}), 404

@chat_bp.route('/chat/users/<user_id>/messages/<message_id>', methods=['DELETE'])
@require_auth
def delete_user_message(user_id, message_id):
    """Delete a message"""
    # Search and delete message
    for channel_id, channel_msgs in messages.items():
        for i, msg in enumerate(channel_msgs):
            if msg['id'] == message_id and msg['sender'] == user_id:
                messages[channel_id].pop(i)
                return '', 204
    
    return jsonify({"error": "Message not found or unauthorized"}), 404

@chat_bp.route('/chat/users/me/messages', methods=['GET'])
@require_auth
def list_my_messages():
    """List messages for the authenticated user"""
    return list_user_messages(request.user.get('id'))

@chat_bp.route('/chat/users/me/messages/<message_id>', methods=['GET'])
@require_auth
def get_my_message(message_id):
    """Get a specific message for the authenticated user"""
    return get_user_message(request.user.get('id'), message_id)

@chat_bp.route('/chat/users/me/messages/<message_id>', methods=['PUT', 'PATCH'])
@require_auth
def update_my_message(message_id):
    """Update authenticated user's message"""
    return update_user_message(request.user.get('id'), message_id)

@chat_bp.route('/chat/users/me/messages/<message_id>', methods=['DELETE'])
@require_auth
def delete_my_message(message_id):
    """Delete authenticated user's message"""
    return delete_user_message(request.user.get('id'), message_id) 