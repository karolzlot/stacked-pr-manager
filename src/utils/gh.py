from github import Github
from src.config.env_vars import GITHUB_ACCESS_TOKEN, GITHUB_REPO
from src.config.logger import logger
from src.models.types import Commit, PRData, Branch

g = Github(GITHUB_ACCESS_TOKEN)
repo = g.get_repo(GITHUB_REPO)

def gh_get_pr_title(pr_number: int) -> str:
    pr = repo.get_pull(pr_number)
    return pr.title




if  __name__ == '__main__':

    t1 = gh_get_pr_title(1)
    print(t1)
    print()


