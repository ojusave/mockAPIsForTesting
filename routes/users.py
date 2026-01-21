from flask import Blueprint, jsonify, request, current_app
from helpers import generate_base_user_data
import random
import os
from datetime import datetime, timedelta
from models.auth import require_auth
from cache_config import cache

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
@require_auth
@cache.cached(timeout=3600, key_prefix='list_users')
def get_data():

    total_records = random.randint(5000, 10000)
    page_size = 30
    page_number = random.randint(1, total_records // page_size)

    base_users = [generate_base_user_data() for _ in range(page_size)]

    response_data = {
        "next_page_token": os.urandom(16).hex(),
        "page_count": total_records // page_size + (1 if total_records % page_size > 0 else 0),
        "page_number": page_number,
        "page_size": page_size,
        "total_records": total_records,
        "users": base_users
    }

    return jsonify(response_data)

@users_bp.route('/users/<user_id>', methods=['GET'])
@cache.memoize(timeout=3600)
@require_auth
def get_user(user_id):
    """Get detailed user information"""
    # Generate random dates within reasonable range
    created_date = datetime.utcnow() - timedelta(days=random.randint(100, 1000))
    last_login = datetime.utcnow() - timedelta(hours=random.randint(1, 240))
    
    # List of possible values for random selection
    roles = ["Admin", "Member", "Owner"]
    timezones = ["Asia/Shanghai", "America/New_York", "Europe/London", "Australia/Sydney"]
    languages = ["en-US", "fr-FR", "es-ES", "de-DE"]
    locations = ["Paris", "New York", "London", "Tokyo", "Sydney"]
    client_versions = ["5.9.6.4993(mac)", "5.9.6.4785(windows)", "5.9.7.1234(linux)"]
    
    # Mock user data with random values
    user = {
        "id": user_id,
        "created_at": created_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dept": "Developers",
        "email": f"user{random.randint(1000,9999)}@example.com",
        "first_name": random.choice(["John", "Jane", "Mike", "Sarah", "David"]),
        "last_client_version": random.choice(client_versions),
        "last_login_time": last_login.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_name": random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones"]),
        "pmi": random.randint(1000000000, 9999999999),
        "role_name": random.choice(roles),
        "timezone": random.choice(timezones),
        "type": random.randint(1, 3),
        "use_pmi": random.choice([True, False]),
        "account_id": os.urandom(8).hex(),
        "account_number": random.randint(10000000, 99999999),
        "cms_user_id": os.urandom(10).hex(),
        "company": "Example Corp",
        "user_created_at": created_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "custom_attributes": [
            {
                "key": os.urandom(12).hex(),
                "name": f"Attribute_{random.randint(1,5)}",
                "value": str(random.randint(1, 100))
            }
        ],
        "employee_unique_id": os.urandom(10).hex(),
        "group_ids": [os.urandom(8).hex() for _ in range(random.randint(1, 3))],
        "im_group_ids": [os.urandom(8).hex() for _ in range(random.randint(1, 3))],
        "jid": f"user{random.randint(1000,9999)}@example.com",
        "job_title": "Software Engineer",
        "cost_center": f"CC-{random.randint(100,999)}",
        "language": random.choice(languages),
        "location": random.choice(locations),
        "login_types": [random.randint(100, 105) for _ in range(random.randint(1, 3))],
        "manager": f"manager{random.randint(100,999)}@example.com",
        "personal_meeting_url": f"https://zoom.us/j/{random.randint(1000000000, 9999999999)}",
        "phone_country": "US",
        "phone_number": f"+1 {random.randint(100,999)}{random.randint(100,999)}{random.randint(1000,9999)}",
        "phone_numbers": [
            {
                "code": "+1",
                "country": "US",
                "label": "Mobile",
                "number": f"{random.randint(100,999)}{random.randint(1000,9999)}",
                "verified": random.choice([True, False])
            }
        ],
        "pic_url": f"https://example.com/photos/{os.urandom(8).hex()}.jpg",
        "plan_united_type": str(random.randint(1, 5)),
        "pronouns": str(random.randint(1000, 9999)),
        "pronouns_option": random.randint(1, 3),
        "role_id": str(random.randint(0, 5)),
        "status": random.choice(["active", "pending", "inactive"]),
        "vanity_url": f"https://zoom.us/{os.urandom(8).hex()}",
        "verified": random.randint(0, 1),
        "cluster": f"us{random.randint(1,10):02d}",
        "zoom_one_type": random.randint(32, 128)
    }
    
    # Add display_name by combining first and last name
    user["display_name"] = f"{user['first_name']} {user['last_name']}"
    
    return jsonify(user)

@users_bp.route('/users/<user_id>/status', methods=['PUT'])
@require_auth
def update_user_status(user_id):
    """Update a user's status (activate/deactivate)"""
    data = request.get_json()
    action = data.get('action')
    
    if action not in ['activate', 'deactivate', 'clock_in', 'clock_out']:
        return jsonify({"error": "Invalid action"}), 400
        
    # Mock response
    return jsonify({}), 200

@users_bp.route('/users/<user_id>/token', methods=['GET'])
@require_auth
def get_user_token(user_id):
    """Get a user's Zoom token or ZAK"""
    token_type = request.args.get('type', 'token')
    ttl = request.args.get('ttl', 7200)
    
    if token_type not in ['token', 'zak']:
        return jsonify({"error": "Invalid token type"}), 400
        
    # Mock response
    response = {
        "token": "6IjAwMDAwMSIsInptX3NrbSI6InptX" 
    }
    return jsonify(response)

@users_bp.route('/users/<user_id>/token', methods=['DELETE']) 
@require_auth
def revoke_user_token(user_id):
    """Revoke a user's SSO token"""
    # Mock response - return 204 for successful deletion
    return '', 204

@users_bp.route('/users/<user_id>/settings/virtual_backgrounds', methods=['POST'])
@require_auth
def upload_virtual_background(user_id):
    """Upload virtual background files for a user"""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    
    # Mock response
    response = {
        "id": "_l0MP1U7Qn2JgJ4oEJbVZQ",
        "is_default": True,
        "name": file.filename,
        "size": 7221,
        "type": "image"
    }
    return jsonify(response), 201

@users_bp.route('/users/<user_id>/settings/virtual_backgrounds', methods=['DELETE'])
@require_auth
def delete_virtual_backgrounds(user_id):
    """Delete virtual background files for a user"""
    file_ids = request.args.get('file_ids')
    
    if not file_ids:
        return jsonify({"error": "file_ids parameter required"}), 400
        
    # Mock response - return 204 for successful deletion
    return '', 204

@users_bp.route('/users/<user_id>', methods=['PATCH'])
def update_user(user_id):
    # After updating user
    cache.delete_memoized(get_user, user_id)
    cache.delete('list_users')
    # ... rest of the code