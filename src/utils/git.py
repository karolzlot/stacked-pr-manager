import re
import subprocess
from pathlib import Path

from dirhash import dirhash

from src.config.env_vars import LOCAL_REPO_PATH
from src.config.logger import logger
from src.models.types import BaseBranch, Branch, Commit, HeadBranch


def _run_git_command(args: list[str]) -> tuple[str, str]:
    all_args: list[str] = ["git", "-C", LOCAL_REPO_PATH] + args
    result = subprocess.run(all_args, capture_output=True, text=True)
    logger.trace(" ".join(all_args))
    logger.trace("-stdout: " + result.stdout.strip())
    if result.stderr:
        logger.trace("#stderr: " + result.stderr.strip())
    assert result.returncode == 0
    return result.stdout.strip(), result.stderr.strip()


def git_checkout(branch: Branch) -> int:
    stdout, stderr = _run_git_command(["checkout", branch])
    assert stderr in [f"Already on '{branch}'", f"Switched to branch '{branch}'"]
    if stdout == f"Your branch is up to date with 'origin/{branch}'.":
        return 0

    pattern = rf"Your branch is behind \'origin/{branch}\' by (\d+) commit(s)?, and can be fast-forwarded."
    match = re.search(pattern, stdout)
    if match:
        num_commits = int(match.group(1))
        return -num_commits

    pattern = rf"Your branch is ahead of \'origin/{branch}\' by (\d+) commit(s)?."
    match = re.search(pattern, stdout)
    if match:
        num_commits = int(match.group(1))
        return num_commits

    raise ValueError(f"Unexpected output from git checkout: {stdout}")


def git_pull(branch: Branch) -> bool:
    assert branch == Branch("main")  # currently only main is needed to be pulled
    # TODO check if it is possible to pull without checkout
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


def git_pull_one_commit(branch: Branch, expected_commit_title: str) -> None:
    """Adapted from https://stackoverflow.com/a/64033792/8896457"""
    assert branch == Branch("main")  # currently only main is needed to be pulled
    assert git_checkout(branch) == -1
    stdout1, stderr1 = _run_git_command(["fetch"])
    assert stdout1 == ""
    assert stderr1 == ""

    stdout2, stderr2 = _run_git_command(["rev-list", f"{branch}..origin/{branch}"])

    assert stderr2 == ""
    assert stdout2 != ""

    local_commit = _git_rev_parse(branch)
    origin_commit = Commit(stdout2)  # the commit that is not on the local branch

    commit_title = get_commit_title(origin_commit)
    assert commit_title == expected_commit_title

    assert git_checkout(branch) == -1  # make sure that it's still true
    stdout3, stderr3 = _run_git_command(["merge", origin_commit])

    assert stderr3 == ""
    assert f"Updating {local_commit[:9]}..{origin_commit[:9]}" in stdout3


def get_commit_title(commit: Commit) -> str:
    """Get first line of commit message"""
    stdout, stderr = _run_git_command(["show", "-s", "--format=%B", commit])
    assert stderr == ""
    return stdout.split("\n")[0]


def git_push(branch: Branch) -> bool:
    # TODO check if it is possible to push without checkout
    # TODO check if it is possible to push (no not-pulled commits on remote etc.)
    assert branch != "main"
    git_checkout(branch)
    # if git_checkout(branch) > 0:
    head_commit_local_before = _git_rev_parse(branch)
    head_commit_origin_before = _git_rev_parse(Branch("origin/" + branch))
    stdout, stderr = _run_git_command(["push"])
    assert stdout == ""
    if stderr == f"Everything up-to-date":
        assert head_commit_local_before == head_commit_origin_before
        return False

    assert head_commit_local_before != head_commit_origin_before

    head_commit_local_after = _git_rev_parse(branch)
    head_commit_origin_after = _git_rev_parse(Branch("origin/" + branch))
    assert (
        head_commit_local_before == head_commit_local_after == head_commit_origin_after
    )

    assert (
        f"{head_commit_origin_before[:9]}..{head_commit_origin_after[:9]}  {branch} -> {branch}"
        in stderr
    )
    assert git_checkout(branch) == 0
    logger.info(f"Pushed {branch}")
    return True


def _git_merge_base(branch1: Branch, branch2: Branch) -> Commit:
    """Find the most recent common ancestor of two branches
    https://stackoverflow.com/questions/1549146/git-find-the-most-recent-common-ancestor-of-two-branches
    """
    stdout, stderr = _run_git_command(["merge-base", branch1, branch2])
    assert stderr == ""
    return Commit(stdout)


def _git_rev_parse(branch: Branch) -> Commit:
    """Get current commit hash
    https://stackoverflow.com/questions/15798862/what-does-git-rev-parse-do
    """
    stdout, stderr = _run_git_command(["rev-parse", branch])
    assert stderr == ""
    return Commit(stdout)


def _git_branch_merged(base_branch: BaseBranch, head_branch: HeadBranch) -> bool:
    """Check if branch 1 is merged into branch 2 (so branch 2 = branch 1 + some commits)
    To merge branch 1 into branch 2, we will need later `git merge branch1` when on branch 2
    https://stackoverflow.com/questions/226976/how-can-i-know-if-a-branch-has-been-already-merged-into-master
    """
    merge_base = _git_merge_base(base_branch, head_branch)
    rev1 = _git_rev_parse(base_branch)
    rev2 = _git_rev_parse(head_branch)

    assert rev2 != merge_base
    assert rev2 != rev1
    if rev1 != merge_base:
        logger.trace(f"Branch {base_branch} is not merged into {head_branch}")
    return rev1 == merge_base


def git_merge_branch_into(base_branch: BaseBranch, head_branch: HeadBranch) -> bool:
    if _git_branch_merged(base_branch, head_branch):
        return False
    git_checkout(head_branch)
    stdout, stderr = _run_git_command(["merge", base_branch])
    assert stderr == ""
    if stdout == f"Already up to date.":
        return False
    elif "Merge made by the 'ort' strategy." in stdout:
        logger.info(f"Branch {base_branch} merged into {head_branch}")
        return True
    else:
        raise ValueError(f"Unexpected output from git merge: {stdout}")


def dirhash_repo() -> str:
    ignore = [".git/", ".venv/", "local/", "__pycache__/"]

    # from dirhash import included_paths
    # included_paths11 = included_paths( Path(LOCAL_REPO_PATH), ignore=ignore)
    # # save to file:
    # with open("included_paths.txt", "w") as f:
    #     for path in included_paths11:
    #         f.write(str(path) + "\n")

    dir_hash = dirhash(Path(LOCAL_REPO_PATH), algorithm="sha1", ignore=ignore)
    assert len(dir_hash) == 40
    return dir_hash


if __name__ == "__main__":
    git_pull_one_commit(Branch("main"), "test")
