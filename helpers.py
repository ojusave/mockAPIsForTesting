import random
import string
import datetime
import uuid
import os
import json
from queue import Queue
from threading import Lock

# Base URL (replace zoom.us with ngrok URL)
BASE_URL = "https://api-endpoint-0f24e0ac73d6.herokuapp.com"

FILES_DIR = 'files'

# Ensure directory exists
os.makedirs(FILES_DIR, exist_ok=True)

# Global variables for file tracking
used_files = set()
available_files = []
file_lock = Lock()

# Expanded list of diverse names
first_names = [
    "John", "Jane", "Michael", "Emily", "David", "Sophia", "Muhammad", "Fatima",
    "Chen", "Yuki", "Raj", "Priya", "Carlos", "Maria", "Kwame", "Zainab",
    "Olga", "Sven", "Aisha", "Ibrahim", "Mei", "Hiroshi", "Ananya", "Rahul",
    "Javier", "Luisa", "Ekundayo", "Chidi", "Alexei", "Natasha", "Hassan", "Amira"
]
last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
]

def initialize_file_list():
    global available_files
    available_files = [f for f in os.listdir(FILES_DIR) if f.endswith('.json')]
    if not available_files:
        raise FileNotFoundError("No JSON files found in the /files directory")

def get_next_file_content():
    global used_files, available_files
    with file_lock:
        if not available_files:
            # All files have been used, reset the list
            used_files.clear()
            initialize_file_list()
        
        file_name = random.choice(available_files)
        available_files.remove(file_name)
        used_files.add(file_name)
        
        file_path = os.path.join(FILES_DIR, file_name)
        with open(file_path, 'r') as file:
            content = json.load(file)
        
        return content, file_name

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + datetime.timedelta(days=random_number_of_days)

def generate_user_id(length=22):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_base_user_data():
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    user_id = generate_user_id()
    return {
        "id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "display_name": f"{first_name} {last_name}",
        "email": f"{first_name.lower()}.{last_name.lower()}@{generate_random_string(5)}.com",
        "type": random.randint(1, 2),
        "zoom_workplace": random.randint(1, 2),
        "on_prem": random.choice([False, True]),
        "pmi": random.randint(1000000000, 9999999999),
        "timezone": random.choice(["America/Los_Angeles", "America/New_York", "Asia/Tokyo", "Europe", "Australia"]),
        "verified": random.randint(0, 1),
        "dept": random.choice(["Engineering", "Sales", "Marketing", "Product"]),
        "created_at": generate_random_date(datetime.datetime(2020, 1, 1), datetime.datetime.now()).isoformat() + "Z",
        "last_login_time": generate_random_date(datetime.datetime(2023, 1, 1), datetime.datetime.now()).isoformat() + "Z",
        "last_client_version": f"{random.randint(5, 6)}.{random.randint(1, 13)}.{random.randint(1000, 9999)}({random.choice(['mac', 'win', 'ipad', 'iphone'])})",
        "pic_url": f"{BASE_URL}/p/{uuid.uuid4()}/{uuid.uuid4()}",
        "language": "en-US",
        "status": random.choice(["active", "inactive"]),
        "role_id": str(random.randint(1, 5)),
        "user_created_at": generate_random_date(datetime.datetime(2020, 1, 1), datetime.datetime.now()).isoformat() + "Z"
    }

# Initialize the file list when the module is loaded
initialize_file_list()