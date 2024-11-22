import os
import subprocess
import requests
import sys
from dotenv import load_dotenv

load_dotenv()

GITLAB_API_URL = "https://gitlab.com/api/v4/projects"
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
GITLAB_USERNAME = os.getenv("GITLAB_USERNAME")
GITLAB_LOCAL_DIR = os.path.expanduser("~/GitLab/")

if not GITLAB_TOKEN or not GITLAB_USERNAME:
    raise ValueError("GitLab token and username must be set in the .env file.")

def create_gitlab_project(project_name):
    """ Create a new project on GitLab using the GitLab API """
    headers = {"Private-Token": GITLAB_TOKEN}
    data = {
        "name": project_name,
        "visibility": "private",
    }
    response = requests.post(GITLAB_API_URL, headers=headers, data=data)    
    if response.status_code == 201:
        print(f"GitLab project '{project_name}' created successfully.")
        return response.json()["http_url_to_repo"]
    else:
        print(f"Failed to create GitLab project. Error: {response.status_code}, {response.text}")
        return None

def push_to_gitlab(local_dir, git_url):
    """ Initialize a git repo, commit, and push the files to GitLab """
    try:
        subprocess.run(["git", "init"], cwd=local_dir, check=True)
        subprocess.run(["git", "add", "."], cwd=local_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=local_dir, check=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=local_dir, check=True)
        subprocess.run(["git", "remote", "add", "origin", git_url], cwd=local_dir, check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=local_dir, check=True)
        print(f"Successfully pushed to GitLab repository: {git_url}")
    except subprocess.CalledProcessError as e:
        print(f"Git error occurred: {e}")

def create_readme(local_dir, project_name):
    """ Create a README file """
    readme_content = f"# {project_name}\n\nHello World from {project_name} project!"
    readme_path = os.path.join(local_dir, "README.md")  
    with open(readme_path, "w") as readme_file:
        readme_file.write(readme_content)
    print(f"README file created at: {readme_path}")

def open_in_vscode(local_dir):
    """ Open the project folder in VS Code """
    subprocess.run(["code", local_dir], check=True)
    print(f"VS Code opened for project: {local_dir}")

def setup_gitlab_project(project_name):
    local_dir = os.path.join(GITLAB_LOCAL_DIR, project_name)
    os.makedirs(local_dir, exist_ok=True)
    create_readme(local_dir, project_name) 
    git_url = create_gitlab_project(project_name)   
    if git_url:
        push_to_gitlab(local_dir, git_url)
        open_in_vscode(local_dir)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 new_project.py <project_name>")
        sys.exit(1)
    project_name = sys.argv[1]
    setup_gitlab_project(project_name)