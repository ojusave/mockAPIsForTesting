import os
from dotenv import load_dotenv
from flask import Flask, send_file, jsonify, Response
from flask_caching import Cache
from asgiref.wsgi import WsgiToAsgi
import uvicorn

from helpers import BASE_URL, fetch_stored_vtt

# Load environment variables
load_dotenv()

# Flask application setup
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Import blueprints
from routes.users import users_bp
from routes.meetings import meetings_bp
from routes.recordings import recordings_bp

# Register blueprints
app.register_blueprint(users_bp)
app.register_blueprint(meetings_bp)
app.register_blueprint(recordings_bp)

# Route to handle download requests for VTT files
@app.route('/rec/download/<path:anything>', methods=['GET'])
def download_vtt(anything):
    meeting_id = anything.split('/')[0]
    vtt_content = fetch_stored_vtt(meeting_id)
    if not vtt_content:
        return jsonify({"error": "VTT not found"}), 404
    return Response(vtt_content, mimetype='text/vtt')

# Example API to simulate meeting data with VTT links
@app.route('/api/meetings/<meeting_id>', methods=['GET'])
def get_meeting_data(meeting_id):
    download_links = {
        "vtt_transcript": f"{BASE_URL}/rec/download/{meeting_id}/transcript.vtt"
    }
    meeting_data = {
        "meeting_id": meeting_id,
        "topic": "Quarterly Review",
        "download_links": download_links
    }
    return jsonify(meeting_data)

# Wrap the Flask app with WSGI to ASGI converter
asgi_app = WsgiToAsgi(app)

# Start the application
if __name__ == '__main__':
    uvicorn.run(asgi_app, host="0.0.0.0", port=8000)