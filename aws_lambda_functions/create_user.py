import gitlab

GITLAB_URL = os.environ.get('GITLAB_URL', '')
PRIVATE_TOKEN = os.environ.get('GITLAB_TOKEN', '')
MAIN_GROUP_ID = 2

def lambda_handler(event, context):
    try:
        name = event.get('name')
        email = event.get('email')
        username = event.get('username')
        password = event.get('password')

        if not all([name, email, username, password]):
            return {"statusCode": 400, "message": "All fields are required."}

        gl = gitlab.Gitlab(GITLAB_URL, private_token=PRIVATE_TOKEN)

        user_data = {
            'name': name,
            'username': username,
            'email': email,
            'password': password,
            'reset_password': False
        }
        user = gl.users.create(user_data)

        group = gl.groups.get(MAIN_GROUP_ID)
        group.members.create({'user_id': user.id, 'access_level': gitlab.REPORTER})

        project = gl.projects.create({
            'name': name,
            'namespace_id': group.id
        })

        return {
            "statusCode": 200,
            "message": "User and repository created successfully!",
            "details": {
                "user_id": user.id,
                "user_email": user.email,
                "project_id": project.id,
                "project_url": project.web_url
            }
        }

    except gitlab.exceptions.GitlabCreateError as e:
        return {"statusCode": 400, "message": f"GitLab API error: {e.error_message}"}

    except Exception as e:
        return {"statusCode": 500, "message": f"An unexpected error occurred: {str(e)}"}