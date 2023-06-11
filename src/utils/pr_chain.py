from src.config.logger import logger
from src.models.types import PRChain
from src.utils.gh import base, head
from src.utils.git import _git_branch_merged, git_merge_branch_into, git_push


def merge_base_into_head(chain: PRChain) -> None:
    """Sync stacked branches in the order they are given"""
    for i in range(len(chain) - 1, -1, -1):
        logger.trace(f"{i=}")
        current_pr = chain[i]
        if _git_branch_merged(base(current_pr), head(current_pr)):
            continue
        else:
            for j in range(i, len(chain)):
                logger.trace(f".{j=}")
                current_pr = chain[j]
                git_merge_branch_into(base(current_pr), head(current_pr))


def push(chain: PRChain) -> None:
    """Push all head branches in PR chain"""
    for pr in chain:
        git_push(head(pr))
