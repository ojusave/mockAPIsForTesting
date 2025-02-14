# Mock APIs

## Overview

This project provides mock API endpoints that simulate a meeting summarization and transcription system. The API mimics functionality similar to the [Zoom API](https://developers.zoom.us/docs/api/), generating random but realistic data for testing and development purposes.

Base URL: `https://zoom-test-apis.onrender.com`

## Authentication

All endpoints require a Bearer token in the Authorization header. Since this is a mock API, **any token value will work**. Simply include:
```
Authorization: Bearer any-token-value
```

## Available Endpoints

### Users
- `GET /users`: Retrieve a list of users
- `GET /users/<user_id>`: Get specific user details
- `POST /users`: Create a new user
- `PUT /users/<user_id>`: Update user details
- `GET /users/<user_id>/status`: Update a user's status (activate/deactivate)
- `GET /users/<user_id>/token`: Get a user's Zoom token or ZAK
- `DELETE /users/<user_id>/token`: Revoke a user's SSO token
- `POST /users/<user_id>/settings/virtual_backgrounds`: Upload virtual background files for a user
- `DELETE /users/<user_id>/settings/virtual_backgrounds`: Delete virtual background files for a user

### Meetings
- `GET /users/<user_id>/meetings`: Get meetings for a specific user
- `GET /meetings/<meeting_id>`: Get specific meeting details
- `POST /meetings`: Create a new meeting
- `GET /meetings/<meeting_id>/meeting_summary`: Get summary for a specific meeting

### Recordings
- `GET /users/<user_id>/recordings`: Get recordings for a specific user
- `GET /recordings/<recording_id>`: Get specific recording details
- `GET /rec/download/<path:path>`: Download VTT transcript file
- `DELETE /recordings/<recording_id>`: Delete a specific recording

### Calendar
- `GET /calendar/events`: Get calendar events
- `POST /calendar/events`: Create calendar event
- `PUT /calendar/events/<event_id>`: Update calendar event
- `DELETE /calendar/events/<event_id>`: Delete a calendar event

### Mail
- `POST /mail/send`: Send email
- `GET /mail/inbox`: Get inbox messages
- `GET /mailboxes/<email>/drafts`: List drafts for a mailbox
- `GET /mailboxes/<email>/labels`: List labels for a mailbox
- `GET /mailboxes/<email>/threads`: List threads for a mailbox
- `DELETE /mailboxes/<email>/drafts/<draft_id>`: Delete a draft

### Chat
- `GET /channels`: List user's chat channels
- `POST /channels`: Create a new chat channel
- `GET /channels/<channel_id>/messages`: Get messages for a channel
- `POST /channels/<channel_id>/messages`: Send a message to a channel
- `GET /channels/<channel_id>/members`: List members in a channel
- `POST /channels/<channel_id>/members`: Add members to a channel
- `GET /channels/<channel_id>`: Get a specific channel
- `PATCH /channels/<channel_id>`: Update a channel's settings
- `DELETE /channels/<channel_id>`: Delete a channel

### Phone
- `GET /account_settings`: Get account settings for phone
- `GET /outbound_caller_id/customized_numbers`: Get customized phone numbers

### Quality Scoring (QSS)
- `GET /qss/score/<meeting_id>`: Get quality score for a meeting
- `POST /qss/feedback`: Submit quality feedback
- `GET /metrics/meetings/<meeting_id>/participants/qos_summary`: Get QoS summary for meeting participants
- `GET /metrics/webinars/<webinar_id>/participants/qos_summary`: Get QoS summary for webinar participants
- `GET /videosdk/sessions/<session_id>/users/qos_summary`: Get QoS summary for session users
- `GET /qss/feedback/<feedback_id>`: Get specific feedback details
- `DELETE /qss/feedback/<feedback_id>`: Delete specific feedback

## Sample API Calls

### Get User Details
```bash
curl -X GET https://zoom-test-apis.onrender.com/users/abc123 \
  -H "Authorization: Bearer any-token-value"
```

Response:
```json
{
    "id": "abc123",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "created_at": "2024-03-20T10:00:00Z",
    "settings": {
        "timezone": "America/New_York",
        "language": "en-US"
    }
}
```

### Get User Meetings
```bash
curl -X GET https://zoom-test-apis.onrender.com/users/abc123/meetings \
  -H "Authorization: Bearer mock-token-123"
```

Response:
```json
{
    "page_size": 30,
    "total_records": 2,
    "meetings": [
        {
            "id": "meeting123",
            "topic": "Weekly Team Sync",
            "start_time": "2024-03-21T15:00:00Z",
            "duration": 60,
            "timezone": "America/New_York",
            "participants": 8,
            "recording_available": true
        },
        {
            "id": "meeting456",
            "topic": "Project Review",
            "start_time": "2024-03-22T14:00:00Z",
            "duration": 45,
            "timezone": "America/New_York",
            "participants": 5,
            "recording_available": false
        }
    ]
}
```

### Get Meeting Summary
```bash
curl -X GET https://zoom-test-apis.onrender.com/meetings/meeting123/meeting_summary \
  -H "Authorization: Bearer any-token-value"
```

Response:
```json
{
    "meeting_id": "meeting123",
    "topic": "Weekly Team Sync",
    "date": "2024-03-21",
    "duration": "1:00:00",
    "summary": {
        "title": "Team Progress and Sprint Planning",
        "overview": "Discussion of current sprint progress and planning for next sprint",
        "key_points": [
            "Completed user authentication module",
            "Started work on API documentation",
            "Identified performance bottlenecks"
        ],
        "action_items": [
            {
                "description": "Review pull request #123",
                "assignee": "John Doe",
                "due_date": "2024-03-23"
            },
            {
                "description": "Update API documentation",
                "assignee": "Jane Smith",
                "due_date": "2024-03-24"
            }
        ]
    },
    "participants": [
        {
            "id": "abc123",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "duration": 3600
        }
    ]
}
```

### Error Response Example
```bash
curl -X GET https://zoom-test-apis.onrender.com/meetings/invalid123/meeting_summary \
  -H "Authorization: Bearer any-token-value"
```

Response:
```json
{
    "error": {
        "code": "404",
        "message": "Meeting not found",
        "details": "No meeting exists with ID: invalid123"
    }
}
```

## Notes

- This is a mock API that generates random but realistic data
- Data is not persistent between requests
- Any Bearer token value will be accepted
- No rate limiting is enforced

For questions or issues, please open a GitHub issue.