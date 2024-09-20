from flask import Blueprint, jsonify, request
from helpers import generate_base_user_data
import random
import os

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
def get_data():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

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