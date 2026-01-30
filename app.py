import os
from flask import Flask, jsonify, Response
from flask_cors import CORS
from asgiref.wsgi import WsgiToAsgi

from config import BASE_URL
from cache_config import cache
from data_store import get_vtt_for_meeting
from routes.users import users_bp
from routes.meetings import meetings_bp
from routes.recordings import recordings_bp
from routes.qss import qss_bp
from routes.calendar import calendar_bp
from routes.phone import phone_bp
from routes.mail import mail_bp
from routes.accounts import accounts_bp
from routes.chat import chat_bp
from routes.webinars import webinars_bp
from routes.reports import reports_bp
from routes.dashboards import dashboards_bp
from routes.devices import devices_bp
from routes.roles import roles_bp
from routes.groups import groups_bp
from routes.tracking_fields import tracking_fields_bp
from routes.rooms import rooms_bp

app = Flask(__name__)
CORS(app)
cache.init_app(app)

# Base URL for API: https://api.zoom.us/v2/ (Zoom API reference)
app.register_blueprint(users_bp, url_prefix="/v2")
app.register_blueprint(meetings_bp, url_prefix="/v2")
app.register_blueprint(recordings_bp, url_prefix="/v2")
app.register_blueprint(qss_bp, url_prefix="/v2")
app.register_blueprint(calendar_bp, url_prefix="/v2")
app.register_blueprint(phone_bp, url_prefix="/v2/phone")
app.register_blueprint(mail_bp, url_prefix="/v2")
app.register_blueprint(accounts_bp, url_prefix="/v2/accounts")
app.register_blueprint(chat_bp, url_prefix="/v2/chat")
app.register_blueprint(webinars_bp, url_prefix="/v2")
app.register_blueprint(reports_bp, url_prefix="/v2")
app.register_blueprint(dashboards_bp, url_prefix="/v2")
app.register_blueprint(devices_bp, url_prefix="/v2")
app.register_blueprint(roles_bp, url_prefix="/v2")
app.register_blueprint(groups_bp, url_prefix="/v2")
app.register_blueprint(tracking_fields_bp, url_prefix="/v2")
app.register_blueprint(rooms_bp, url_prefix="/v2")

# Recording transcript download and cache (under /v2 to match Zoom base URL)
@app.route("/v2/rec/download/<path:path>", methods=["GET"])
def download_vtt(path):
    parts = path.split("/")
    if len(parts) != 2 or parts[1] != "transcript.vtt":
        return jsonify({"error": {"code": "400", "message": "Invalid VTT path; use {meeting_id}/transcript.vtt"}}), 400
    meeting_id = parts[0]
    vtt_data = get_vtt_for_meeting(meeting_id)
    if not vtt_data:
        return jsonify({"error": {"code": "404", "message": "VTT not found", "details": f"No transcript for meeting: {meeting_id}"}}), 404
    return Response(vtt_data, mimetype="text/vtt")

@app.route("/v2/cache/clear", methods=["POST"])
def clear_cache():
    try:
        cache.clear()
        return jsonify({"message": "Cache cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": {"code": "500", "message": str(e)}}), 500


@app.route("/v2/cache/clear/<key>", methods=["POST"])
def clear_cache_key(key):
    try:
        cache.delete(key)
        return jsonify({"message": f"Cache key {key} cleared"}), 200
    except Exception as e:
        return jsonify({"error": {"code": "500", "message": str(e)}}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": {"code": "404", "message": "Resource not found", "details": "The requested URL was not found"}
    }), 404


asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(asgi_app, host="0.0.0.0", port=8000)