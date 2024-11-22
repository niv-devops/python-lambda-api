import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from dotenv import load_dotenv

load_dotenv()

GITLAB_API_BASE_URL = "http://localhost:9090/api/v4"
GROUP_ID = os.getenv("GROUP_ID")
GITLAB_TOKEN = os.getenv("GITLAB_SERVER_TOKEN")
GOOGLE_SHEET_NAME = "Python script GitLab"

HEADERS = {
    "Authorization": f"Bearer {GITLAB_TOKEN}"
}

def setup_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client

def parse_google_sheet():
    client = setup_google_sheets()
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    employees = sheet.get_all_records()
    return employees

def create_gitlab_user(name, username, email, password):
    data = {
        "name": name,
        "username": username,
        "email": email,
        "password": password,
        "skip_confirmation": True
    }
    response = requests.post(f"{GITLAB_API_BASE_URL}/users", headers=HEADERS, json=data)
    if response.status_code == 201:
        user_id = response.json()["id"]
        print(f"GitLab user created: {username} (ID: {user_id})")
        return user_id
    else:
        print(f"Failed to create GitLab user: {response.status_code}, {response.json()}")
        return None

def add_user_to_group(user_id):
    data = {
        "user_id": user_id,
        "access_level": 20  # "Reporter" role
    }
    response = requests.post(f"{GITLAB_API_BASE_URL}/groups/{GROUP_ID}/members", headers=HEADERS, json=data)
    if response.status_code == 201:
        print(f"User added to group with Reporter role (User ID: {user_id})")
    else:
        print(f"Failed to add user to group: {response.status_code}, {response.json()}")

def create_user_repository(username):
    data = {
        "name": username,
        "visibility": "private"
    }
    response = requests.post(f"{GITLAB_API_BASE_URL}/projects", headers=HEADERS, json=data)
    if response.status_code == 201:
        repo_url = response.json()["http_url_to_repo"]
        print(f"Repository created for {username}: {repo_url}")
    else:
        print(f"Failed to create repository for {username}: {response.status_code}, {response.json()}")

if __name__ == "__main__":
    employees = parse_google_sheet()
    for employee in employees:
        name = employee["Name"]
        username = employee["Username"]
        email = employee["Email"]
        password = employee["Password"]
        
        print(f"Processing employee: {name}")
        
        user_id = create_gitlab_user(name, username, email, password)
        if user_id:
            add_user_to_group(user_id)
            create_user_repository(username)