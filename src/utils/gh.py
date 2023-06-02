from github import Github
from github.PullRequest import PullRequest
from src.config.env_vars import GITHUB_ACCESS_TOKEN, GITHUB_REPO, BRANCH_PREFIX, GITHUB_USERNAME
from src.config.logger import logger
from src.models.types import PullRequestBlueprint, PRChain
import questionary as q
from questionary import Choice
from tabulate import tabulate
from time import sleep
from typing import Optional, List

g = Github(GITHUB_ACCESS_TOKEN)
repo = g.get_repo(GITHUB_REPO)


def gh_get_pr_title(pr_number: int) -> str:
    pr = repo.get_pull(pr_number)
    return pr.title


def create_gh_pr(pr_blueprint: PullRequestBlueprint, silent:bool=False) -> Optional[int]:
    
    logger.info(f"Creating PR from {pr_blueprint.head} to {pr_blueprint.base} ({pr_blueprint.title})")
        
    if not silent and not q.confirm(f"Create this PR?", default=False, auto_enter=False).ask():
        logger.info("Aborting")
        return None
    
    # make sure that branches begin with user's prefix (except `main`):
    assert pr_blueprint.head.startswith(BRANCH_PREFIX)
    assert pr_blueprint.base.startswith(BRANCH_PREFIX) or pr_blueprint.base == "main"

    # make sure that the target branches exist:
    assert repo.get_branch(pr_blueprint.head)
    assert repo.get_branch(pr_blueprint.base)
    
    sleep(3)
    pr = repo.create_pull(
        title=pr_blueprint.title,
        body="",
        head=pr_blueprint.head,
        base=pr_blueprint.base,
        draft=True,
    )
    
    logger.info(f"Created PR #{pr.number}: {pr.title}")
    sleep(3)

    return pr.number


def create_gh_prs(pr_blueprints: list[PullRequestBlueprint]) -> list[int]:
    """Create Pull Requests from a list of PullRequestBlueprints."""
    pr_numbers = []

    table = []
    for pr_blueprint in pr_blueprints:
        table.append([pr_blueprint.head, pr_blueprint.base, pr_blueprint.title])
    logger.info("Plan: \n" + tabulate(table, headers=["Source", "Target", "Title"]))

    if not q.confirm(f"Create PRs according to above plan?", default=False, auto_enter=False).ask():
        logger.info("Aborting")
        return []

    for pr_blueprint in pr_blueprints:
        pr_number = create_gh_pr(pr_blueprint, silent=True)
        if pr_number:
            pr_numbers.append(pr_number)
    logger.info(f"Created PRs: {pr_numbers}")
    return pr_numbers


def get_user_opened_prs() -> list[PullRequest]:
    """Find users's PRs."""
    prs = repo.get_pulls(state="open")
    user_prs = []
    for pr in prs:
        if pr.user.login == GITHUB_USERNAME:
            user_prs.append(pr)
    return user_prs


def get_pr_chains(prs: List[PullRequest]) -> List[PRChain]:
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
            if len(chain) > 1 and (pr.head.label not in chains_dict or len(chain) > len(chains_dict[pr.head.label])):
                chains_dict[pr.head.label] = chain

    chains_dict = {}
    for pr in prs:
        dfs(pr, PRChain([]), chains_dict)
    
    return list(chains_dict.values())


def select_pr_chain(chains: List[PRChain]) -> Optional[PRChain]:
    """Prompt the user to select a chain of PRs."""
    if not chains:
        print("No chains to select.")
        return None

    options = [" -> ".join([pr.title for pr in chain]) for chain in chains]
    selection = q.select("Choose a chain:", choices=options).ask()

    return chains[options.index(selection)] if selection else None


def select_pr_chain_from_user_opened_prs() -> Optional[PRChain]:
    """Prompt the user to select a chain of PRs from user's opened PRs."""
    prs = get_user_opened_prs()
    chains = get_pr_chains(prs)
    return select_pr_chain(chains)



if  __name__ == '__main__':

    pass
    # t1 = gh_get_pr_title(1)
    # print(t1)
    # print()
