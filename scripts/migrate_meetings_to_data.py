#!/usr/bin/env python3
"""Migrate files/*.json (summary + vtt_data) into data/meetings/<id>.json (Zoom meeting + summary + vtt + recording_files + participants)."""
import os
import json
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES_DIR = os.path.join(BASE_DIR, "files")
MEETINGS_DIR = os.path.join(BASE_DIR, "data", "meetings")
BASE_URL = "https://api.zoom.us"

# file basename -> meeting_id, host_id
MAPPING = [
    ("1", "m1", "u1"), ("2", "m2", "u1"), ("3", "m3", "u1"), ("4", "m4", "u1"),
    ("5", "m5", "u2"), ("6", "m6", "u2"), ("7", "m7", "u2"), ("8", "m8", "u2"),
    ("9", "m9", "u3"), ("10", "m10", "u3"), ("11", "m11", "u3"), ("example", "m_example", "u3"),
]


def main():
    os.makedirs(MEETINGS_DIR, exist_ok=True)
    for file_stem, meeting_id, host_id in MAPPING:
        path = os.path.join(FILES_DIR, f"{file_stem}.json")
        if not os.path.isfile(path):
            print(f"Skip {path} (not found)")
            continue
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        summary = raw.get("summary") or {}
        vtt_data = raw.get("vtt_data") or ""
        if not vtt_data.strip().upper().startswith("WEBVTT"):
            vtt_data = "WEBVTT\n\n" + vtt_data
        topic = summary.get("summary_title") or f"Meeting {meeting_id}"
        start_time = "2026-01-15T14:00:00Z"
        duration = 60
        rec_id_1 = str(uuid.uuid4())
        rec_id_2 = str(uuid.uuid4())
        recording_files = [
            {
                "id": rec_id_1,
                "meeting_id": meeting_id,
                "recording_start": start_time,
                "recording_end": "2026-01-15T15:00:00Z",
                "file_type": "TRANSCRIPT",
                "file_extension": "VTT",
                "file_size": len(vtt_data),
                "play_url": f"{BASE_URL}/rec/play/{rec_id_1[:8]}",
                "download_url": f"{BASE_URL}/rec/download/{meeting_id}/transcript.vtt",
                "status": "completed",
                "recording_type": "shared_screen_with_speaker_view",
            },
            {
                "id": rec_id_2,
                "meeting_id": meeting_id,
                "recording_start": start_time,
                "recording_end": "2026-01-15T15:00:00Z",
                "file_type": "MP4",
                "file_extension": "MP4",
                "file_size": 50000000,
                "play_url": f"{BASE_URL}/rec/play/{rec_id_2[:8]}",
                "download_url": f"{BASE_URL}/rec/download/{meeting_id}/recording.mp4",
                "status": "completed",
                "recording_type": "shared_screen_with_speaker_view",
            },
        ]
        participants = [
            {"id": "p1", "name": "Alice Chen", "user_id": "u1", "user_email": "alice.chen@zoom-mock.com", "join_time": start_time, "leave_time": "2026-01-15T15:00:00Z", "duration": 3600},
            {"id": "p2", "name": "Bob Martinez", "user_id": "u2", "user_email": "bob.martinez@zoom-mock.com", "join_time": start_time, "leave_time": "2026-01-15T15:00:00Z", "duration": 3600},
        ]
        payload = {
            "uuid": meeting_id,
            "id": meeting_id,
            "host_id": host_id,
            "host_email": f"{host_id}@zoom-mock.com",
            "topic": topic,
            "type": 2,
            "start_time": start_time,
            "duration": duration,
            "timezone": "America/New_York",
            "created_at": "2026-01-01T00:00:00Z",
            "join_url": f"{BASE_URL}/j/{meeting_id}",
            "start_url": f"{BASE_URL}/s/{meeting_id}",
            "password": "abc123",
            "agenda": summary.get("summary_overview", "")[:200],
            "settings": {
                "host_video": True,
                "participant_video": False,
                "join_before_host": False,
                "mute_upon_entry": True,
                "waiting_room": True,
                "meeting_authentication": False,
            },
            "summary": summary,
            "vtt_data": vtt_data,
            "recording_files": recording_files,
            "participants": participants,
        }
        out_path = os.path.join(MEETINGS_DIR, f"{meeting_id}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"Wrote {out_path}")
    print("Done.")


if __name__ == "__main__":
    main()
