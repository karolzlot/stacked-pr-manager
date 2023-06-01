from dotenv import load_dotenv
import os

load_dotenv()

github_access_token= os.getenv('GITHUB_ACCESS_TOKEN')
local_repo_path= os.getenv('LOCAL_REPO_PATH')
github_repo = os.getenv('GITHUB_REPO')

assert isinstance(github_access_token, str)
assert isinstance(local_repo_path, str)
assert isinstance(github_repo, str)

GITHUB_ACCESS_TOKEN = github_access_token
LOCAL_REPO_PATH = local_repo_path
GITHUB_REPO = github_repo


