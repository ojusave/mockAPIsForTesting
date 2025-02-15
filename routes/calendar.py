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
def create_acl_rule(cal_id):
    """Create a new ACL rule"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    data = request.get_json()
    if not data or 'scope' not in data or 'role' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    acl_rule = {
        "kind": "calendar#aclRule",
        "etag": f"\"{generate_random_string(20)}\"",
        "id": f"user:{generate_random_string(10)}@zoom.com",
        "scope": data['scope'],
        "role": data['role']
    }
    return jsonify(acl_rule), 200

@calendar_bp.route('/calendars/<cal_id>/acl/<acl_id>', methods=['DELETE'])
def delete_acl_rule(cal_id, acl_id):
    """Delete an existing ACL rule"""
    # Logic to delete the ACL rule
    return '', 204

@calendar_bp.route('/calendars/<cal_id>/acl/<acl_id>', methods=['GET'])
def get_acl_rule(cal_id, acl_id):
    """Get the specified ACL rule"""
    acl_rule = {
        "kind": "calendar#aclRule",
        "etag": f"\"{generate_random_string(20)}\"",
        "id": acl_id,
        "scope": {
            "type": "user",
            "value": f"{generate_random_string(8)}@zoom.us"
        },
        "role": "reader"
    }
    return jsonify(acl_rule), 200

@calendar_bp.route('/calendars/<cal_id>/acl', methods=['GET'])
def list_acl_rules(cal_id):
    """List ACL rules of specified calendar"""
    acl_rules = []
    for _ in range(random.randint(1, 5)):
        acl_rules.append({
            "kind": "calendar#aclRule",
            "etag": f"\"{generate_random_string(20)}\"",
            "id": f"user:{generate_random_string(10)}@zoom.com",
            "scope": {
                "type": random.choice(["user", "group", "domain"]),
                "value": f"{generate_random_string(8)}@zoom.us"
            },
            "role": random.choice(["none", "freeBusyReader", "reader", "writer", "owner"])
        })
    return jsonify({"kind": "calendar#acl", "items": acl_rules}), 200

@calendar_bp.route('/calendars/users/<user_id>/calendarList', methods=['GET'])
def list_user_calendars(user_id):
    """List the calendars in the user's own calendarList"""
    calendars = []
    for _ in range(random.randint(1, 10)):
        calendars.append(generate_calendar_entry())
    return jsonify({"kind": "calendar#calendarList", "items": calendars}), 200

@calendar_bp.route('/calendars', methods=['POST'])
def create_calendar():
    """Create a new secondary calendar"""
    data = request.get_json()
    if not data or 'summary' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    new_calendar = {
        "kind": "calendar#calendar",
        "etag": f"\"{generate_random_string(20)}\"",
        "id": f"{generate_random_string(10)}@zoom.com",
        "summary": data['summary'],
        "timeZone": "America/Los_Angeles",
        "description": "calendar description",
        "location": "San Jose"
    }
    return jsonify(new_calendar), 200

@calendar_bp.route('/calendars/<cal_id>', methods=['DELETE'])
def delete_calendar(cal_id):
    """Delete a calendar owned by a user"""
    return '', 204

@calendar_bp.route('/calendars/<cal_id>', methods=['GET'])
def get_calendar(cal_id):
    """Get the specified calendar"""
    calendar = {
        "kind": "calendar#calendar",
        "etag": f"\"{generate_random_string(20)}\"",
        "id": cal_id,
        "summary": "My calendar",
        "timeZone": "America/Los_Angeles",
        "description": "calendar description",
        "location": "San Jose"
    }
    return jsonify(calendar), 200

@calendar_bp.route('/calendars/<cal_id>', methods=['PATCH'])
def update_calendar(cal_id):
    """Update the specified calendar"""
    data = request.get_json()
    updated_calendar = {
        "kind": "calendar#calendar",
        "etag": f"\"{generate_random_string(20)}\"",
        "id": cal_id,
        "summary": data.get('summary', "Updated calendar"),
        "timeZone": data.get('timeZone', "America/Los_Angeles"),
        "description": data.get('description', "Updated description"),
        "location": data.get('location', "Updated location")
    }
    return jsonify(updated_calendar), 200

@calendar_bp.route('/calendars/colors', methods=['GET'])
def get_calendar_colors():
    """Get the color definitions for calendars and events"""
    colors = {
        "kind": "calendar#colors",
        "calendar": [{"color_id": "1", "value": {"foreground": "#FD3D4A", "background": "#F7F9FA"}}],
        "event": [{"color_id": "1", "value": {"foreground": "#FD3D4A", "background": "#F7F9FA"}}]
    }
    return jsonify(colors), 200

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

@calendar_bp.route('/calendars/<cal_id>/events/<event_id>', methods=['DELETE'])
def delete_event(cal_id, event_id):
    """Delete an existing event from the specified calendar"""
    # Logic to delete the event
    return '', 204

@calendar_bp.route('/calendars/<cal_id>/events/<event_id>', methods=['GET'])
def get_event(cal_id, event_id):
    """Get the specified event on the specified calendar"""
    # Set future dates for the event
    future_start = datetime.datetime.now() + datetime.timedelta(days=1)  # 1 day in the future
    future_end = future_start + datetime.timedelta(hours=1)  # 1 hour after the start

    event = {
        "kind": "calendar#event",
        "etag": f"\"{generate_random_string(20)}\"",
        "id": event_id,
        "summary": "event title",
        "description": "event description",
        "location": "San Jose",
        "start": {
            "dateTime": future_start.isoformat() + "Z",
            "timeZone": "America/Los_Angeles"
        },
        "end": {
            "dateTime": future_end.isoformat() + "Z",
            "timeZone": "America/Los_Angeles"
        },
        "attendees": [
            {
                "email": "mark.joe@zoom.com",
                "displayName": "Mark Joe",
                "optional": False,
                "responseStatus": "needsAction"
            }
        ],
        "status": "confirmed",
        "visibility": "default"
    }
    return jsonify(event), 200

@calendar_bp.route('/calendars/<cal_id>/events/import', methods=['POST'])
def import_event(cal_id):
    """Import event to the specified calendar"""
    data = request.get_json()
    if not data or 'start' not in data or 'end' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    imported_event = {
        "kind": "calendar#event",
        "etag": f"\"{generate_random_string(20)}\"",
        "id": f"{generate_random_string(10)}@zoom.com",
        "summary": data.get('summary', "Imported Event"),
        "description": data.get('description', ""),
        "location": data.get('location', ""),
        "start": data['start'],
        "end": data['end'],
        "attendees": data.get('attendees', []),
        "status": data.get('status', "confirmed"),
        "visibility": data.get('visibility', "default")
    }
    return jsonify(imported_event), 200

@calendar_bp.route('/calendars/<cal_id>/events/quickAdd', methods=['POST'])
def quick_add_event(cal_id):
    """Quick add an event to the specified calendar"""
    text = request.args.get('text')
    if not text:
        return jsonify({"error": "Missing required query parameter: text"}), 400

    # Logic to parse the text and create an event
    quick_event = {
        "kind": "calendar#event",
        "etag": f"\"{generate_random_string(20)}\"",
        "id": f"{generate_random_string(10)}@zoom.com",
        "summary": text,
        "start": {
            "dateTime": "2020-01-01T00:00:00Z",
            "timeZone": "America/Los_Angeles"
        },
        "end": {
            "dateTime": "2020-01-01T01:00:00Z",
            "timeZone": "America/Los_Angeles"
        }
    }
    return jsonify(quick_event), 200

@calendar_bp.route('/calendars/<cal_id>/events/<event_id>/move', methods=['POST'])
def move_event(cal_id, event_id):
    """Move the specified event from a calendar to another specified calendar"""
    destination = request.args.get('destination')
    if not destination:
        return jsonify({"error": "Missing required query parameter: destination"}), 400

    # Logic to move the event
    moved_event = {
        "kind": "calendar#event",
        "etag": f"\"{generate_random_string(20)}\"",
        "id": event_id,
        "summary": "Moved Event",
        "start": {
            "dateTime": "2020-01-01T00:00:00Z",
            "timeZone": "America/Los_Angeles"
        },
        "end": {
            "dateTime": "2020-01-01T01:00:00Z",
            "timeZone": "America/Los_Angeles"
        }
    }
    return jsonify(moved_event), 200

@calendar_bp.route('/calendars/<cal_id>/events', methods=['GET'])
def list_events(cal_id):
    """List events on the specified calendar"""
    events = []
    for _ in range(random.randint(1, 5)):
        future_start = datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 30))  # Random future date
        future_end = future_start + datetime.timedelta(hours=1)  # 1 hour after the start
        events.append({
            "kind": "calendar#event",
            "etag": f"\"{generate_random_string(20)}\"",
            "id": f"{generate_random_string(10)}@zoom.com",
            "summary": f"Event {generate_random_string(5)}",
            "start": {
                "dateTime": future_start.isoformat() + "Z",
                "timeZone": "America/Los_Angeles"
            },
            "end": {
                "dateTime": future_end.isoformat() + "Z",
                "timeZone": "America/Los_Angeles"
            }
        })
    return jsonify({"kind": "calendar#events", "items": events}), 200 