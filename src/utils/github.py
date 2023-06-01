from github import Github
from src.config.env_vars import GITHUB_ACCESS_TOKEN, GITHUB_REPO

def gh_get_pr_title(pr_number: int) -> str:
    g = Github(GITHUB_ACCESS_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
    pr = repo.get_pull(pr_number)
    return pr.title
