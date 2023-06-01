import re
import subprocess
from pathlib import Path


from dirhash import dirhash
from src.config.logger import logger
from src.config.env_vars import LOCAL_REPO_PATH
from src.models.types import Branch, PRData, Commit


def _run_git_command(args: list[str]) -> tuple[str, str]:
    all_args: list[str] = ["git", "-C", LOCAL_REPO_PATH] + args
    result = subprocess.run(all_args, capture_output=True, text=True)
    logger.trace(' '.join(all_args))
    logger.trace("-stdout: "+result.stdout.strip())
    if result.stderr:
        logger.trace("#stderr: "+result.stderr.strip())
    assert result.returncode == 0
    return result.stdout.strip(), result.stderr.strip()
    
def git_checkout(branch: Branch) -> int:
    assert branch.isidentifier()
    stdout, stderr = _run_git_command(["checkout", branch])
    assert stderr in [f"Already on '{branch}'",
            f"Switched to branch '{branch}'"]
    if stdout == f"Your branch is up to date with 'origin/{branch}'.":
        return 0
    
    pattern = rf'Your branch is behind \'origin/{branch}\' by (\d+) commits, and can be fast-forwarded.'
    match = re.search(pattern, stdout)
    if match:
        num_commits = int(match.group(1))
        return -num_commits
        
    pattern = rf'Your branch is ahead of \'origin/{branch}\' by (\d+) commits.'
    match = re.search(pattern, stdout)
    if match:
        num_commits = int(match.group(1))
        return num_commits

    raise ValueError(f"Unexpected output from git checkout: {stdout}")

def git_pull(branch: Branch) -> bool:
    # TODO check if it is possible to pull without checkout
    assert branch.isidentifier()
    git_checkout(branch)
    # if git_checkout(branch) < 0:
    stdout, stderr = _run_git_command(["pull"])
    assert stderr == "" or "[new branch]" in stderr
    if stdout == f"Already up to date.":
        return False
    elif "Updating " in stdout:
        logger.info(stdout)
        assert git_checkout(branch) == 0
        return True
    else:
        raise ValueError(f"Unexpected output from git pull: {stdout}")

def git_push(branch: Branch) -> bool:
    # TODO check if it is possible to push without checkout
    assert branch.isidentifier()
    assert branch != "main"
    git_checkout(branch)
    # if git_checkout(branch) > 0:
    stdout, stderr = _run_git_command(["push"])
    assert stdout == ""
    if stderr == f"Everything up-to-date":
        return False
    assert "remote: Resolving deltas:" in stderr
    assert git_checkout(branch) == 0
    return True


def _git_merge_base(branch1: Branch, branch2: Branch) -> Commit:
    """Find the most recent common ancestor of two branches
    https://stackoverflow.com/questions/1549146/git-find-the-most-recent-common-ancestor-of-two-branches
    """
    assert branch1.isidentifier()
    assert branch2.isidentifier()
    stdout, stderr = _run_git_command(["merge-base", branch1, branch2])
    assert stderr == ""
    assert len(stdout) == 40
    assert stdout.isidentifier()
    assert re.match(r"[0-9a-f]{40}", stdout)
    return Commit(stdout)


def _git_rev_parse(branch: Branch) -> Commit:
    """Get current commit hash
    https://stackoverflow.com/questions/15798862/what-does-git-rev-parse-do
    """
    assert branch.isidentifier()
    stdout, stderr = _run_git_command(["rev-parse", branch])
    assert stderr == ""
    assert len(stdout) == 40
    assert stdout.isidentifier()
    assert re.match(r"[0-9a-f]{40}", stdout)
    return Commit(stdout)


def _git_branch_merged(branch1: Branch, branch2: Branch) -> bool:
    """Check if branch 1 is merged into branch 2 (so branch 2 = branch 1 + some commits)
    To merge branch 1 into branch 2, we will need later `git merge branch1` when on branch 2
    https://stackoverflow.com/questions/226976/how-can-i-know-if-a-branch-has-been-already-merged-into-master
    """
    assert branch1.isidentifier()
    assert branch2.isidentifier()
    merge_base = _git_merge_base(branch1, branch2)
    rev1 = _git_rev_parse(branch1)
    rev2 = _git_rev_parse(branch2)

    assert rev2 != merge_base
    assert rev2 != rev1
    if rev1 != merge_base:
        logger.debug(f"Branch {branch1} is not merged into {branch2}")
    return rev1 == merge_base

def git_merge_branch_into(branch1: Branch, branch2: Branch) -> bool:
    assert branch1.isidentifier()
    assert branch2.isidentifier()
    if _git_branch_merged(branch1, branch2):
        return False
    git_checkout(branch2)
    stdout, stderr = _run_git_command(["merge", branch1])
    assert stderr == ""
    if stdout == f"Already up to date.":
        return False
    elif "Merge made by the 'ort' strategy." in stdout:
        logger.info(f"Branch {branch1} merged into {branch2}") 
        return True
    else:
        raise ValueError(f"Unexpected output from git merge: {stdout}")
    
def sync_stacked_branches(prs: list[PRData] ) -> None:
    """Sync stacked branches in the order they are given
    """

    for i in range(len(prs)-1, -1, -1):
        pr = prs[i]
        print(i)
        if _git_branch_merged(prs[i]["target"], prs[i]["branch"]):
            continue
        else:
            for j in range(i, len(prs)):
                print(j)
                git_merge_branch_into(prs[j]["target"], prs[j]["branch"])

def dirhash_repo() -> str:
    ignore = [".git/", ".venv/", "local/", "__pycache__/"]

    # from dirhash import included_paths
    # included_paths11 = included_paths( Path(LOCAL_REPO_PATH), ignore=ignore)
    # # save to file:
    # with open("included_paths.txt", "w") as f:
    #     for path in included_paths11:
    #         f.write(str(path) + "\n")

    dir_hash = dirhash( Path(LOCAL_REPO_PATH), algorithm="sha1", ignore=ignore)
    assert len(dir_hash) == 40
    return dir_hash


def push_branches(prs: list[PRData]) -> None:
    """Pull all branches
    """
    for pr in prs:
        git_push(pr["branch"])