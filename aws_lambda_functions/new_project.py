import gitlab
import os

GITLAB_URL = "https://gitlab.com"
PRIVATE_TOKEN = os.environ['GITLAB_TOKEN']

def lambda_handler(event, context):
    try:
        project_name = event.get('project_name')
        if not project_name:
            return {"statusCode": 400, "message": "Project name is required."}
        
        gl = gitlab.Gitlab(GITLAB_URL, private_token=PRIVATE_TOKEN)
        project = gl.projects.create({'name': project_name})
        readme_content = f"# {project_name}\n\nHello, World!"
        project.files.create({
            'file_path': 'README.md',
            'branch': 'main',
            'content': readme_content,
            'commit_message': 'Initial commit: Add README.md'
        })    
        return {
            "statusCode": 200,
            "message": f"Project '{project_name}' created successfully!",
            "details": {
                "project_id": project.id,
                "project_url": project.web_url
            }
        }
    
    except gitlab.exceptions.GitlabCreateError as e:
        return {"statusCode": 400, "message": f"GitLab API error: {e.error_message}"}
    
    except Exception as e:
        return {"statusCode": 500, "message": f"An unexpected error occurred: {str(e)}"}


""" Test Event:
{
  "project_name": "LmabdaTest"
}
"""