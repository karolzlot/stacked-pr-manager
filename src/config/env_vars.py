from dotenv import load_dotenv
import os

load_dotenv()

def get_env(name: str) -> str:
    env = os.getenv(name)
    assert env is not None
    assert len(env) > 0
    return env

GITHUB_ACCESS_TOKEN = get_env('GITHUB_ACCESS_TOKEN')
LOCAL_REPO_PATH = get_env('LOCAL_REPO_PATH')
GITHUB_REPO = get_env('GITHUB_REPO')
GITHUB_USERNAME = get_env('GITHUB_USERNAME')

REVIEWERS= get_env('REVIEWERS').split(',')
BRANCH_PREFIX= get_env('BRANCH_PREFIX')

assert len(REVIEWERS) > 0
assert len(BRANCH_PREFIX) > 0