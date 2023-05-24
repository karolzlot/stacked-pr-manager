import os, sys
import re
import time
import subprocess
from pathlib import Path
from typing import Union, NewType
from ruamel.yaml import YAML
from dotenv import load_dotenv
from github import Github
from dirhash import dirhash
from loguru import logger
from time import sleep

Branch = NewType('Branch', str)
Commit = NewType('Commit', str)

load_dotenv()


GITHUB_ACCESS_TOKEN= os.getenv('GITHUB_ACCESS_TOKEN')
LOCAL_REPO_PATH= os.getenv('LOCAL_REPO_PATH')
GITHUB_REPO= os.getenv('GITHUB_REPO')
assert GITHUB_ACCESS_TOKEN and LOCAL_REPO_PATH and GITHUB_REPO

def read_prs_config_file() -> list[dict[str, Union[str,int]]]:
    config_file = Path('prs.yaml')
    if not config_file.exists():
        raise FileNotFoundError('prs.yaml file not found.')

    with open(config_file, 'r') as file:
        yaml = YAML(typ='safe')
        config_data = yaml.load(file)

    if not isinstance(config_data, list):
        raise ValueError('Invalid format in prs.yaml file.')

    return config_data


def gh_get_pr_title(pr_number: int) -> str:
    g = Github(GITHUB_ACCESS_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
    pr = repo.get_pull(pr_number)
    return pr.title


def _run_git_command(args: list[str]) -> tuple[str, str]:
    all_args: list[str] = ["git", "-C", LOCAL_REPO_PATH] + args
    result = subprocess.run(all_args, capture_output=True, text=True, check=True)
    logger.debug(' '.join(all_args))
    logger.trace(result.stdout.strip())
    if result.stderr:
        logger.trace(result.stderr.strip())
    assert result.returncode == 0
    return result.stdout.strip(), result.stderr.strip()
    
def git_checkout(branch: Branch) -> int:
    assert not " " in branch
    stdout, stderr = _run_git_command(["checkout", branch])
    assert stderr in [f"Already on '{branch}'",
            f"Switched to branch '{branch}'"]
    if stdout == f"Your branch is up to date with 'origin/{branch}'.":
        return 0
    else:
        pattern = rf'Your branch is behind \'origin/{branch}\' by (\d+) commits, and can be fast-forwarded.'
        match = re.search(pattern, stdout)
        if match:
            num_commits = int(match.group(1))
            return num_commits
        else:
            raise ValueError(f"Unexpected output from git checkout: {stdout}")
    
def git_pull(branch: Branch) -> bool:
    # TODO check if it is possible to pull without checkout
    git_checkout(branch)
    # if git_checkout(branch) > 0:
    stdout, stderr = _run_git_command(["pull"])
    assert stderr == "" or "[new branch]" in stderr
    if stdout == f"Already up to date.":
        return False
    elif "Updating " in stdout:
        logger.warning(stdout)
        return True
    else:
        raise ValueError(f"Unexpected output from git pull: {stdout}")

def _git_merge_base(branch1: Branch, branch2: Branch) -> Commit:
    """Find the most recent common ancestor of two branches
    https://stackoverflow.com/questions/1549146/git-find-the-most-recent-common-ancestor-of-two-branches
    """
    stdout, stderr = _run_git_command(["merge-base", branch1, branch2])
    assert stderr == ""
    assert len(stdout) == 40
    assert not " " in stdout
    assert re.match(r"[0-9a-f]{40}", stdout)
    return Commit(stdout)


def _git_rev_parse(branch: Branch) -> Commit:
    """Get current commit hash
    https://stackoverflow.com/questions/15798862/what-does-git-rev-parse-do
    """
    stdout, stderr = _run_git_command(["rev-parse", branch])
    assert stderr == ""
    assert len(stdout) == 40
    assert not " " in stdout
    assert re.match(r"[0-9a-f]{40}", stdout)
    return Commit(stdout)





if __name__ == '__main__':

    pass

