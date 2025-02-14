from flask import Blueprint, jsonify, request
from helpers import generate_random_string
import datetime
import random

calendar_bp = Blueprint('calendar', __name__)

def generate_calendar_entry():
    """Generate a random calendar list entry"""
    return {
        "kind": "calendar#calendarListEntry",
        "etag": f"\"{generate_random_string(20)}\"",
        "id": f"{generate_random_string(10)}@zoom.com",
        "summary": f"Calendar {generate_random_string(5)}",
        "description": "Calendar description",
        "location": random.choice(["San Jose", "New York", "London", "Tokyo"]),
        "timeZone": random.choice(["America/Los_Angeles", "America/New_York", "Europe/London", "Asia/Tokyo"]),
        "colorId": str(random.randint(1, 10)),
        "backgroundColor": f"#{generate_random_string(6)}",
        "foregroundColor": "#ffffff",
        "hidden": random.choice([True, False]),
        "selected": random.choice([True, False]),
        "accessRole": random.choice(["freeBusyReader", "reader", "writer", "owner"]),
        "defaultReminders": [
            {
                "method": random.choice(["email", "popup"]),
                "minutes": random.randint(5, 60)
            }
        ]
    }

@calendar_bp.route('/calendars/<cal_id>/acl', methods=['GET'])
def get_calendar_acl(cal_id):
    """List ACL rules of specified calendar"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    max_results = int(request.args.get('maxResults', 250))
    show_deleted = request.args.get('showDeleted', 'false').lower() == 'true'

    acl_rules = []
    num_rules = random.randint(1, 5)
    
    for _ in range(num_rules):
        rule = {
            "kind": "calendar#aclRule",
            "etag": f"\"{generate_random_string(20)}\"",
            "id": f"user:{generate_random_string(10)}@zoom.com",
            "scope": {
                "type": random.choice(["user", "group", "domain"]),
                "value": f"{generate_random_string(8)}@zoom.us"
            },
            "role": random.choice(["none", "freeBusyReader", "reader", "writer", "owner"])
        }
        acl_rules.append(rule)

    response = {
        "kind": "calendar#acl",
        "etag": f"\"{generate_random_string(20)}\"",
        "items": acl_rules
    }

    return jsonify(response)

@calendar_bp.route('/calendars/<cal_id>/acl', methods=['POST'])
def create_calendar_acl(cal_id):
    """Create a new ACL rule"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    data = request.get_json()
    if not data or 'role' not in data or 'scope' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    response = {
        "kind": "calendar#aclRule",
        "etag": f"\"{generate_random_string(20)}\"",
        "id": f"user:{generate_random_string(10)}@zoom.com",
        "scope": data['scope'],
        "role": data['role']
    }

    return jsonify(response)

@calendar_bp.route('/calendars/users/<user_id>/calendarList', methods=['GET'])
def get_calendar_list(user_id):
    """List calendars in user's calendar list"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    max_results = int(request.args.get('maxResults', 250))
    min_access_role = request.args.get('minAccessRole')

    calendars = []
    num_calendars = random.randint(1, 10)
    
    for _ in range(num_calendars):
        calendars.append(generate_calendar_entry())

    response = {
        "kind": "calendar#calendarList",
        "etag": f"\"{generate_random_string(20)}\"",
        "items": calendars
    }

    return jsonify(response)

@calendar_bp.route('/calendars/freeBusy', methods=['POST'])
def query_freebusy():
    """Query free/busy information"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    data = request.get_json()
    if not data or 'timeMin' not in data or 'timeMax' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    calendars = {}
    for item in data.get('items', []):
        cal_id = item.get('id')
        if cal_id:
            busy_periods = []
            num_periods = random.randint(0, 5)
            
            for _ in range(num_periods):
                start_time = datetime.datetime.fromisoformat(data['timeMin'].replace('Z', ''))
                end_time = datetime.datetime.fromisoformat(data['timeMax'].replace('Z', ''))
                
                random_start = start_time + datetime.timedelta(hours=random.randint(0, 24))
                random_end = random_start + datetime.timedelta(hours=random.randint(1, 3))
                
                if random_end <= end_time:
                    busy_periods.append({
                        "start": random_start.isoformat() + "Z",
                        "end": random_end.isoformat() + "Z"
                    })
            
            calendars[cal_id] = {"busy": busy_periods}

    response = {
        "kind": "calendar#freeBusy",
        "timeMin": data['timeMin'],
        "timeMax": data['timeMax'],
        "calendars": calendars
    }

    return jsonify(response) 