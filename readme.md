# Mock APIs

## Overview

This project implements a mock API service that simulates a meeting summarization and transcription system. It provides endpoints for user management, meeting data, recordings, transcripts, meeting summaries, calendar integration, mail services, and quality scoring. The API is designed to mimic the functionality of a real-time meeting platform, generating random but realistic data for testing and development purposes.

The mock endpoints are inspired by the [Zoom API](https://developers.zoom.us/docs/api/) architecture.

## Features

- User management and authentication
- Meeting data retrieval and management
- Recording information and downloads
- Transcript (VTT) generation and download
- Meeting summaries
- Calendar integration
- Mail service integration
- Quality scoring system (QSS)

## Tech Stack

- Python 3.x
- Flask (Web framework)
- Flask-Caching (For caching)
- ASGI (Asynchronous Server Gateway Interface)
- Uvicorn (ASGI server)

## Project Structure

```
├── app.py
├── helpers.py
├── models/
│   └── auth.py
├── routes/
│   ├── users.py
│   ├── meetings.py
│   ├── recordings.py
│   ├── calendar.py
│   ├── mail.py
│   └── qss.py
├── files/
│   └── (JSON files with meeting data)
├── .env
└── requirements.txt
```

## Setup and Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <project-directory>
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   BASE_URL=https://api-endpoint-0f24e0ac73d6.herokuapp.com
   ```

5. Prepare JSON files:
   Place your JSON files containing meeting data in the `files/` directory.

## Running the Application

To start the server, run:

```
python app.py
```

The server will start on `http://0.0.0.0:8000`.

## API Endpoints

### Authentication Note
All endpoints require a Bearer token in the Authorization header, but since this is a mock API, **any token value will work**. Simply include:
```
Authorization: Bearer any-token-value
```

### Users
- `GET /users`: Retrieve a list of users ([Zoom Users API](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/users))
- `GET /users/<user_id>`: Get specific user details ([Zoom User Details](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/user))
- `POST /users`: Create a new user ([Zoom Create User](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/userCreate))
- `PUT /users/<user_id>`: Update user details ([Zoom Update User](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/userUpdate))

### Meetings
- `GET /users/<user_id>/meetings`: Get meetings for a specific user ([Zoom List Meetings](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/meetings))
- `GET /meetings/<meeting_id>`: Get specific meeting details ([Zoom Meeting Details](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/meeting))
- `POST /meetings`: Create a new meeting ([Zoom Create Meeting](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/meetingCreate))
- `GET /meetings/<meeting_id>/meeting_summary`: Get summary for a specific meeting ([Zoom Meeting Summary](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/dashboardMeetingDetails))

### Recordings
- `GET /users/<user_id>/recordings`: Get recordings for a specific user ([Zoom List Recordings](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/recordingsList))
- `GET /recordings/<recording_id>`: Get specific recording details ([Zoom Recording Details](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/recordingGet))
- `GET /rec/download/<path:path>`: Download VTT transcript file ([Zoom Get Transcript](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/recordingRegistrantQuestionGet))

### Calendar
- `GET /calendar/events`: Get calendar events ([Zoom Schedule Meeting](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/meetingCreate))
- `POST /calendar/events`: Create calendar event
- `PUT /calendar/events/<event_id>`: Update calendar event

### Mail
- `POST /mail/send`: Send email ([Zoom Invitation Email](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/meetingInvitationEmail))
- `GET /mail/inbox`: Get inbox messages

### Quality Scoring (QSS)
- `GET /qss/score/<meeting_id>`: Get quality score for a meeting ([Zoom QoS Details](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/qosParticipants))
- `POST /qss/feedback`: Submit quality feedback

## Response Format Examples

### Meeting Summary Response
```json
{
    "meeting_id": "123",
    "summary": {
        "title": "Project Planning Meeting",
        "overview": "Discussion of Q2 objectives",
        "key_points": [...],
        "action_items": [...]
    }
}
```

### Recording Response
```json
{
    "recording_id": "456",
    "meeting_id": "123",
    "duration": "1:30:00",
    "download_url": "/rec/download/456.vtt",
    "created_at": "2024-03-20T10:00:00Z"
}
```

## Data Generation

The API generates random but realistic data for all endpoints. This includes:

- User profiles and authentication data
- Meeting details and summaries
- Recording information
- Transcripts (VTT files)
- Calendar events
- Mail messages
- Quality scores

Data is generated on-the-fly and is not persistent between requests.

## Caching

The application uses Flask-Caching to improve performance. The cache is configured as a simple in-memory store with the following features:
- Cache timeout: 300 seconds
- Maximum items: 100
- Cache key prefix: 'mock_api'

## Error Handling

The API includes comprehensive error handling for:

- Authentication failures
- Missing or invalid tokens
- Invalid request parameters
- Resource not found errors
- Rate limiting
- Server errors

Each error response includes:
- HTTP status code
- Error message
- Error code
- Additional details when applicable

## Security Notes

This is a mock API that implements minimal security measures for demonstration purposes:
- Bearer token is required but any value will work
- No real authentication is performed
- No rate limiting is enforced

For production use, proper security measures should be implemented.

## Contributing

Contributions to improve the mock API are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature-name`)
6. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Sample API Calls

### Users
```bash
# Get User Details
curl -X GET http://0.0.0.0:8000/users/abc123 \
  -H "Authorization: Bearer any-token-value"

# Response
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

### Meetings
```bash
# Get User Meetings
curl -X GET http://0.0.0.0:8000/users/abc123/meetings \
  -H "Authorization: Bearer mock-token-123"

# Response
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

### Recordings
```bash
# Get Meeting Recording
curl -X GET http://0.0.0.0:8000/recordings/rec789 \
  -H "Authorization: Bearer any-token-value"

# Response
{
    "recording_id": "rec789",
    "meeting_id": "meeting123",
    "topic": "Weekly Team Sync",
    "start_time": "2024-03-21T15:00:00Z",
    "duration": 3600,
    "files": [
        {
            "id": "file123",
            "file_type": "VTT",
            "download_url": "/rec/download/file123.vtt",
            "file_size": 256000
        },
        {
            "id": "file456",
            "file_type": "MP4",
            "download_url": "/rec/download/file456.mp4",
            "file_size": 128000000
        }
    ]
}
```

### Meeting Summary
```bash
# Get Meeting Summary
curl -X GET http://0.0.0.0:8000/meetings/meeting123/meeting_summary \
  -H "Authorization: Bearer any-token-value"

# Response
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
# Invalid Meeting ID
curl -X GET http://0.0.0.0:8000/meetings/invalid123/meeting_summary \
  -H "Authorization: Bearer any-token-value"

# Response
{
    "error": {
        "code": "404",
        "message": "Meeting not found",
        "details": "No meeting exists with ID: invalid123"
    }
}
```