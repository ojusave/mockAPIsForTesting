# Mock APIs

## Overview

This project implements a mock API service that simulates a meeting summarization and transcription system. It provides endpoints for user management, meeting data, recordings, transcripts, and meeting summaries. The API is designed to mimic the functionality of a real-time meeting platform, generating random but realistic data for testing and development purposes.

## Features

- User management
- Meeting data retrieval
- Recording information
- Transcript (VTT) generation and download
- Meeting summaries

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
├── routes/
│   ├── users.py
│   ├── meetings.py
│   └── recordings.py
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

### 1. List Users
- `GET /users`: Retrieve a list of users

### 2. List User Meetings
- `GET /users/<user_id>/meetings`: Get meetings for a specific user

### 3. List User Recordings
- `GET /users/<user_id>/recordings`: Get recordings for a specific user

### 4. List Meeting Recordings
- Included in the response of `GET /users/<user_id>/recordings`

### 5. List Meeting Summaries
- `GET /meetings/<meeting_id>/meeting_summary`: Get summary for a specific meeting

### 6. Download VTT Files
- `GET /rec/download/<path:path>`: Download VTT transcript file

## Data Generation

The API generates random but realistic data for all endpoints. This includes:

- User profiles
- Meeting details
- Recording information
- Transcripts (VTT files)
- Meeting summaries

Data is generated on-the-fly and is not persistent between requests.

## Meeting Summaries

Meeting summaries are generated for each meeting and include:

- Summary title
- Summary overview
- Detailed summary points
- Next steps or action items

These summaries are designed to provide a concise overview of the meeting content, key discussion points, and outcomes.

## Caching

The application uses Flask-Caching to improve performance. The cache is configured as a simple in-memory store.

## Error Handling

The API includes basic error handling for common scenarios such as:

- Missing authorization token
- Invalid date formats
- File not found errors

## Security Notes

This is a mock API and does not implement real security measures. In a production environment, proper authentication and authorization should be implemented.

## Contributing

Contributions to improve the mock API are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature-name`)
6. Create a new Pull Request