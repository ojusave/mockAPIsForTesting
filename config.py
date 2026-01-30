"""
Application configuration. Centralizes env and constants for Zoom-style mock API.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Base URL for links in responses (e.g. join_url, download_url)
BASE_URL = os.getenv("BASE_URL", "https://api.zoom.us")

# Default date range for list endpoints (year 2026)
DEFAULT_DATE_FROM = "2026-01-01"
DEFAULT_DATE_TO = "2026-12-31"

# Pagination defaults (Zoom-style)
DEFAULT_PAGE_SIZE = 30
MAX_PAGE_SIZE = 300

# Cache
CACHE_TIMEOUT = 3600
CACHE_KEY_PREFIX = "zoom_mock_"

# Data directory: Zoom-style accounts, users, meetings (API reads from here)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_ACCOUNTS = os.path.join(DATA_DIR, "accounts.json")
DATA_USERS_DIR = os.path.join(DATA_DIR, "users")
DATA_MEETINGS_DIR = os.path.join(DATA_DIR, "meetings")
