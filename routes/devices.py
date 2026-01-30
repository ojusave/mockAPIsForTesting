"""
Zoom Devices / H.323/SIP API stubs. Mirrors Zoom REST: devices.
"""
from flask import Blueprint, jsonify, request
from models.auth import require_auth
from helpers import generate_random_string

devices_bp = Blueprint("devices", __name__)


@devices_bp.route("/devices", methods=["GET"])
@require_auth
def list_devices():
    """List H.323/SIP devices. Query: page_size, next_page_token."""
    page_size = min(int(request.args.get("page_size", 30)), 300)
    return jsonify({
        "page_size": page_size,
        "next_page_token": "",
        "devices": [
            {"id": "device1", "name": "Room Device 1", "protocol": "H.323", "ip": "192.168.1.1", "encryption": True}
        ],
    })


@devices_bp.route("/devices", methods=["POST"])
@require_auth
def create_device():
    """Create H.323/SIP device. Body: name, protocol, ip, encryption."""
    data = request.get_json() or {}
    device_id = generate_random_string(16)
    return jsonify({
        "id": device_id,
        "name": data.get("name", "New Device"),
        "protocol": data.get("protocol", "H.323"),
        "ip": data.get("ip", "0.0.0.0"),
        "encryption": data.get("encryption", True),
    }), 201


@devices_bp.route("/devices/<device_id>", methods=["GET"])
@require_auth
def get_device(device_id):
    """Get device by ID."""
    return jsonify({"id": device_id, "name": "Device", "protocol": "H.323", "ip": "192.168.1.1", "encryption": True})


@devices_bp.route("/devices/<device_id>", methods=["PATCH"])
@require_auth
def update_device(device_id):
    """Update device."""
    data = request.get_json() or {}
    return jsonify({"id": device_id, "name": data.get("name", "Device"), "protocol": "H.323", "ip": data.get("ip", "192.168.1.1"), "encryption": data.get("encryption", True)}), 200


@devices_bp.route("/devices/<device_id>", methods=["DELETE"])
@require_auth
def delete_device(device_id):
    """Delete device."""
    return "", 204
