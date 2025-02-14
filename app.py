import os
from dotenv import load_dotenv
from flask import Flask, send_file, jsonify, Response
from flask_caching import Cache
from asgiref.wsgi import WsgiToAsgi
import uvicorn

from helpers import BASE_URL, get_next_file_content
from routes.qss import qss_bp
from routes.calendar import calendar_bp
from routes.phone import phone_bp
from routes.mail import mail_bp
from routes.accounts import accounts_bp

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
app.register_blueprint(qss_bp)
app.register_blueprint(calendar_bp)
app.register_blueprint(phone_bp, url_prefix='/v2/phone')
app.register_blueprint(mail_bp, url_prefix='/v2/emails')
app.register_blueprint(accounts_bp, url_prefix='/accounts')

# Global dictionary to store VTT content for each meeting
vtt_storage = {}

# Route to handle download requests for VTT files
@app.route('/rec/download/<path:anything>', methods=['GET'])
def download_vtt(anything):
    parts = anything.split('/')
    if len(parts) != 2 or parts[1] != 'transcript.vtt':
        return jsonify({"error": "Invalid VTT request"}), 400

    meeting_id = parts[0]
    
    if meeting_id not in vtt_storage:
        # If VTT not in storage, get new file content
        try:
            file_content, _ = get_next_file_content()
            vtt_data = file_content.get('vtt_data', '')
            if vtt_data:
                vtt_storage[meeting_id] = vtt_data
            else:
                return jsonify({"error": "VTT not found in file"}), 404
        except Exception as e:
            return jsonify({"error": f"Error fetching VTT: {str(e)}"}), 500

    vtt_content = vtt_storage.get(meeting_id)
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