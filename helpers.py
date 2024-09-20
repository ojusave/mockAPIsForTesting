import random
import string
import datetime
import uuid
import os
import requests
import json
import threading
import time
from queue import Queue

# Base URL (replace zoom.us with ngrok URL)
BASE_URL = "https://8a2325d6f247.ngrok.app"

# Cerebras API settings
CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY", "csk-92wemnmk5y2962tjcdk55kph5edhhknnhe9382r8kt2rk4eh")
CEREBRAS_API_URL = "https://api.cerebras.ai/v1/chat/completions"

VTT_FILES_DIR = 'vtt_files'
SUMMARIES_DIR = 'summary_files'

# Ensure directories exist
os.makedirs(VTT_FILES_DIR, exist_ok=True)
os.makedirs(SUMMARIES_DIR, exist_ok=True)

# Global storage for pre-generated content
_pre_generated_content = []
content_queue = Queue()

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

# List of realistic meeting topics
meeting_topics = [
    "Quarterly Financial Review", "Product Roadmap Planning", "Team Building Workshop",
    "Customer Feedback Analysis", "Marketing Strategy Session", "IT Infrastructure Upgrade",
    "Employee Onboarding Process", "Sales Pipeline Review", "Agile Sprint Planning",
    "Diversity and Inclusion Initiative", "Budget Allocation Discussion",
    "New Market Expansion Opportunities", "Quality Assurance Procedures",
    "Environmental Sustainability Measures", "Remote Work Policy Update",
    "Data Privacy Compliance Training", "Supply Chain Optimization",
    "Customer Service Improvement Strategies", "Employee Wellness Program",
    "Artificial Intelligence Integration", "Corporate Social Responsibility",
    "Risk Management Assessment", "Cybersecurity Threat Analysis",
    "Talent Acquisition Strategies", "Product Launch Preparation",
    "Competitor Analysis Presentation", "Crisis Management Protocol",
    "Innovation Brainstorming Session", "Performance Review Standardization",
    "Brand Identity Refresh Discussion"
]

# Helper function to generate a random string
def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Helper function to generate a random date between two dates
def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + datetime.timedelta(days=random_number_of_days)

# Generate user data
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

def generate_cerebras_content(meeting_id, meeting_topic, meeting_duration):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CEREBRAS_API_KEY}"
    }

    # Generate VTT content
    vtt_prompt = f"Generate a VTT (WebVTT) transcript for a {meeting_duration}-minute meeting about '{meeting_topic}'. Include timestamps and speaker names from the following list: {', '.join(random.sample(first_names, 5))}."
    vtt_payload = {
        "model": "llama3.1-70b",
        "stream": False,
        "messages": [{"content": vtt_prompt, "role": "user"}],
        "temperature": 0.7,
        "max_tokens": -1,
        "seed": random.randint(0, 1000000),
        "top_p": 1
    }

    try:
        vtt_response = requests.post(CEREBRAS_API_URL, headers=headers, data=json.dumps(vtt_payload))
        vtt_response.raise_for_status()
        vtt_content = vtt_response.json()['choices'][0]['message']['content']
    except requests.RequestException as e:
        print(f"Error generating VTT content: {e}")
        vtt_content = f"Error generating VTT for meeting {meeting_id}"

    # Generate meeting summary
    summary_prompt = f"Generate a summary for a meeting with the topic '{meeting_topic}' that lasted {meeting_duration} minutes. Include an overview and next steps. Base this summary on the following VTT content:\n\n{vtt_content}"
    summary_payload = {
        "model": "llama3.1-8b",
        "stream": False,
        "messages": [{"content": summary_prompt, "role": "user"}],
        "temperature": 0.7,
        "max_tokens": -1,
        "seed": random.randint(0, 1000000),
        "top_p": 1
    }

    try:
        summary_response = requests.post(CEREBRAS_API_URL, headers=headers, data=json.dumps(summary_payload))
        summary_response.raise_for_status()
        summary_content = summary_response.json()['choices'][0]['message']['content']
    except requests.RequestException as e:
        print(f"Error generating summary content: {e}")
        summary_content = f"Error generating summary for meeting {meeting_id}"

    return vtt_content, summary_content

def store_generated_content(meeting_id, meeting_topic, vtt_content, summary_content):
    # Store VTT content
    with open(os.path.join(VTT_FILES_DIR, f"{meeting_id}.vtt"), "w") as vtt_file:
        vtt_file.write(vtt_content)
    
    # Store summary content
    with open(os.path.join(SUMMARIES_DIR, f"{meeting_id}.json"), "w") as summary_file:
        json.dump({"meeting_topic": meeting_topic, "summary": summary_content}, summary_file)
    
    # Add to pre-generated content list
    _pre_generated_content.append({
        "meeting_id": meeting_id,
        "meeting_topic": meeting_topic,
        "vtt_content": vtt_content,
        "summary_content": summary_content
    })

    # Add to content queue
    content_queue.put({
        "meeting_id": meeting_id,
        "meeting_topic": meeting_topic,
        "vtt_content": vtt_content,
        "summary_content": summary_content
    })

def fetch_stored_vtt(meeting_id):
    vtt_file_path = os.path.join(VTT_FILES_DIR, f"{meeting_id}.vtt")
    if os.path.exists(vtt_file_path):
        with open(vtt_file_path, "r") as vtt_file:
            return vtt_file.read()
    return None

def fetch_stored_summary(meeting_id):
    summary_file_path = os.path.join(SUMMARIES_DIR, f"{meeting_id}.json")
    if os.path.exists(summary_file_path):
        with open(summary_file_path, "r") as summary_file:
            return json.load(summary_file)
    return None

def get_random_pre_generated_content():
    if not _pre_generated_content:
        return content_queue.get()  # Wait for content to be generated
    return random.choice(_pre_generated_content)

def pre_generate_content():
    for _ in range(100):
        meeting_id = generate_random_string(10)
        meeting_topic = random.choice(meeting_topics)
        meeting_duration = random.randint(30, 120)
        
        vtt_content, summary_content = generate_cerebras_content(meeting_id, meeting_topic, meeting_duration)
        store_generated_content(meeting_id, meeting_topic, vtt_content, summary_content)
        
        time.sleep(1)  # Add a small delay to avoid overwhelming the Cerebras API

# Start pre-generation in a separate thread
threading.Thread(target=pre_generate_content, daemon=True).start()