"""Zoom Chat API. Source of truth: data/chat_channels.json, data/chat_messages.json."""
from flask import Blueprint, jsonify, request
from models.auth import require_auth
from cache_config import cache
import time
from data_store import load_chat_channels, save_chat_channels, load_chat_messages, save_chat_messages
from helpers import generate_random_string

chat_bp = Blueprint("chat", __name__)


def _get_mock_user_id():
    """Mock user ID for chat; in real Zoom API this comes from token."""
    return getattr(request, "user", None) and request.user.get("id") or "mock_user_id"


@chat_bp.route("/channels", methods=["GET"])
@require_auth
def list_channels():
    """List user's chat channels."""
    channels = load_chat_channels()
    ch_list = list(channels.values())
    return jsonify({
        "channels": ch_list,
        "page_size": len(ch_list),
        "total_records": len(ch_list),
    })


@chat_bp.route("/channels", methods=["POST"])
@require_auth
def create_channel():
    """Create channel. Body: name (required), type (1=private, 2=private_with_owner, 3=public, 4=instant), channel_settings."""
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": {"code": "400", "message": "Validation failed", "details": "name is required"}}), 400
    channels = load_chat_channels()
    channel_id = str(len(channels) + 1) if channels else "1"
    while channel_id in channels:
        channel_id = generate_random_string(8)
    new_channel = {
        "id": channel_id,
        "name": data["name"],
        "type": data.get("type", 1),
        "channel_settings": data.get("channel_settings") or {},
    }
    channels[channel_id] = new_channel
    save_chat_channels(channels)
    return jsonify(new_channel), 201


@chat_bp.route("/channels/<channel_id>/messages", methods=["GET"])
@require_auth
def get_messages(channel_id):
    """List messages. Query: page_size, next_page_token, to_contact (optional)."""
    channels = load_chat_channels()
    messages = load_chat_messages()
    if channel_id not in channels:
        return jsonify({"error": {"code": "404", "message": "Channel not found"}}), 404
    channel_messages = messages.get(channel_id, [])
    total = len(channel_messages)
    page_size = min(int(request.args.get("page_size", 50)), 200)
    next_page_token = request.args.get("next_page_token", "")
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
    channels = load_chat_channels()
    messages = load_chat_messages()
    if channel_id not in channels:
        return jsonify({"error": {"code": "404", "message": "Channel not found"}}), 404
    data = request.get_json() or {}
    if not data.get("message") and not data.get("content"):
        return jsonify({"error": {"code": "400", "message": "Validation failed", "details": "message or content is required"}}), 400
    channel_messages = messages.get(channel_id, [])
    message = {
        "id": str(len(channel_messages) + 1),
        "message": data.get("message") or data.get("content", ""),
        "sender": _get_mock_user_id(),
        "timestamp": int(time.time() * 1000),
    }
    channel_messages.append(message)
    messages[channel_id] = channel_messages
    save_chat_messages(messages)
    return jsonify(message), 201


@chat_bp.route("/channels/<channel_id>/members", methods=["GET"])
@require_auth
def list_members(channel_id):
    """List members in a channel."""
    channels = load_chat_channels()
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
    return jsonify({"members": [], "page_size": 0, "total_records": 0})


@chat_bp.route("/channels/<channel_id>/members", methods=["POST"])
@require_auth
def add_members(channel_id):
    """Add members to a channel."""
    channels = load_chat_channels()
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
    return jsonify({"added_at": int(time.time() * 1000), "ids": []}), 201


@chat_bp.route("/channels/<channel_id>", methods=["GET"])
@require_auth
def get_channel(channel_id):
    """Get a specific channel."""
    channels = load_chat_channels()
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
    return jsonify(channels[channel_id])


@chat_bp.route("/channels/<channel_id>", methods=["PATCH"])
@require_auth
def update_channel(channel_id):
    """Update a channel's settings."""
    channels = load_chat_channels()
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
    data = request.get_json() or {}
    channel = dict(channels[channel_id])
    if "name" in data:
        channel["name"] = data["name"]
    if "channel_settings" in data:
        channel["channel_settings"] = dict(channel.get("channel_settings", {}), **data["channel_settings"])
    channels[channel_id] = channel
    save_chat_channels(channels)
    return "", 204


@chat_bp.route("/channels/<channel_id>", methods=["DELETE"])
@require_auth
def delete_channel(channel_id):
    """Delete a channel."""
    channels = load_chat_channels()
    messages = load_chat_messages()
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
    channels = {k: v for k, v in channels.items() if k != channel_id}
    if channel_id in messages:
        messages = {k: v for k, v in messages.items() if k != channel_id}
    save_chat_channels(channels)
    save_chat_messages(messages)
    return "", 204


@chat_bp.route("/channels/<channel_id>/members/<member_id>", methods=["DELETE"])
@require_auth
def remove_member(channel_id, member_id):
    """Remove a member from a channel."""
    channels = load_chat_channels()
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
    return "", 204


@chat_bp.route("/channels/search", methods=["POST"])
@require_auth
def search_channels():
    """Search for channels."""
    data = request.get_json() or {}
    needle = data.get("needle", "")
    channels = load_chat_channels()
    found_channels = [ch for ch in channels.values() if needle.lower() in ch.get("name", "").lower()]
    return jsonify({
        "channels": found_channels,
        "page_size": len(found_channels),
        "total_records": len(found_channels),
    })


@chat_bp.route("/channels/<channel_id>/members/me", methods=["POST"])
@require_auth
def join_channel(channel_id):
    """Join a channel."""
    channels = load_chat_channels()
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
    return jsonify({
        "added_at": int(time.time() * 1000),
        "id": _get_mock_user_id(),
        "member_id": f"member_{_get_mock_user_id()}",
    }), 201


@chat_bp.route("/channels/<channel_id>/members/me", methods=["DELETE"])
@require_auth
def leave_channel(channel_id):
    """Leave a channel."""
    channels = load_chat_channels()
    if channel_id not in channels:
        return jsonify({"error": "Channel not found"}), 404
    return "", 204


@chat_bp.route("/chat/users/<user_id>/messages", methods=["GET"])
@require_auth
@cache.memoize(timeout=3600)
def list_user_messages(user_id):
    """List messages for a specific user."""
    messages = load_chat_messages()
    user_messages = []
    for channel_msgs in messages.values():
        user_messages.extend([msg for msg in channel_msgs if msg.get("sender") == user_id])
    return jsonify({
        "messages": user_messages,
        "page_size": len(user_messages),
        "next_page_token": None,
    })


@chat_bp.route("/chat/users/<user_id>/messages", methods=["POST"])
@require_auth
def send_user_message(user_id):
    """Send a direct message to a user."""
    data = request.get_json() or {}
    messages = load_chat_messages()
    dm_key = "_direct_messages"
    direct = messages.get(dm_key, [])
    message = {
        "id": f"msg_{int(time.time())}",
        "message": data.get("message", ""),
        "sender": _get_mock_user_id(),
        "receiver": user_id,
        "timestamp": int(time.time() * 1000),
    }
    direct.append(message)
    messages[dm_key] = direct
    save_chat_messages(messages)
    cache.delete_memoized(list_user_messages, user_id)
    return jsonify(message), 201


@chat_bp.route("/chat/users/<user_id>/messages/<message_id>", methods=["GET"])
@chat_bp.route("/chat/users/<user_id>/messages/<message_id>", methods=["PUT", "PATCH"])
@chat_bp.route("/chat/users/<user_id>/messages/<message_id>", methods=["DELETE"])
@require_auth
def get_user_message(user_id, message_id):
    """Get a specific message."""
    messages = load_chat_messages()
    for channel_msgs in messages.values():
        for msg in channel_msgs:
            if str(msg.get("id")) == str(message_id) and (msg.get("sender") == user_id or msg.get("receiver") == user_id):
                return jsonify(msg)
    return jsonify({"error": "Message not found"}), 404


@chat_bp.route("/chat/users/me/messages", methods=["GET"])
@require_auth
def list_my_messages():
    """List messages for the authenticated user."""
    return list_user_messages(_get_mock_user_id())


@chat_bp.route("/chat/users/me/messages/<message_id>", methods=["GET"])
@require_auth
def get_my_message(message_id):
    """Get a specific message for the authenticated user."""
    return get_user_message(_get_mock_user_id(), message_id)


@chat_bp.route("/chat/users/me/messages/<message_id>", methods=["PUT", "PATCH"])
@require_auth
def update_my_message(message_id):
    """Update authenticated user's message."""
    data = request.get_json() or {}
    messages = load_chat_messages()
    for ch_id, channel_msgs in list(messages.items()):
        for i, msg in enumerate(channel_msgs):
            if str(msg.get("id")) == str(message_id) and msg.get("sender") == _get_mock_user_id():
                channel_msgs[i] = dict(msg, **{k: v for k, v in data.items() if k in ("message",)})
                save_chat_messages(messages)
                return jsonify(channel_msgs[i])
    return jsonify({"error": {"code": "404", "message": "Message not found"}}), 404


@chat_bp.route("/chat/users/me/messages/<message_id>", methods=["DELETE"])
@require_auth
def delete_my_message(message_id):
    """Delete authenticated user's message."""
    messages = load_chat_messages()
    for ch_id, channel_msgs in list(messages.items()):
        for i, msg in enumerate(channel_msgs):
            if str(msg.get("id")) == str(message_id) and msg.get("sender") == _get_mock_user_id():
                channel_msgs.pop(i)
                messages[ch_id] = channel_msgs
                save_chat_messages(messages)
                return "", 204
    return jsonify({"error": {"code": "404", "message": "Message not found"}}), 404
