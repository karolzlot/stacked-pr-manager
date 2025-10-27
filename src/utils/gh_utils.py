from github.PullRequest import PullRequest

from src.config.logger import logger
from src.models.types import PRChain, PullRequest


def get_pr_chains(prs: list[PullRequest]) -> list[PRChain]:
    """Find chains of PRs."""
    pr_dict = {pr.base.label: [] for pr in prs}
    for pr in prs:
        pr_dict[pr.base.label].append(pr)

    def dfs(pr: PullRequest, chain: PRChain, chains_dict: dict) -> None:
        chain.append(pr)
        if pr.head.label in pr_dict:
            for next_pr in pr_dict[pr.head.label]:
                dfs(next_pr, PRChain(chain.copy()), chains_dict)
        else:
            if len(chain) > 1 and (
                pr.head.label not in chains_dict
                or len(chain) > len(chains_dict[pr.head.label])
            ):
                chains_dict[pr.head.label] = chain

    chains_dict = {}
    for pr in prs:
        dfs(pr, PRChain([]), chains_dict)

    return list(chains_dict.values())
