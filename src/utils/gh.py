from time import sleep

import questionary as q
from github import Github
from github.PullRequest import PullRequest
from tabulate import tabulate

from src.config.env_vars import (
    BRANCH_PREFIX,
    GITHUB_ACCESS_TOKEN,
    GITHUB_REPO,
    GITHUB_USERNAME,
    REVIEWERS,
)
from src.config.logger import logger
from src.models.types import (
    BaseBranch,
    HeadBranch,
    PRChain,
    PullRequest,
    PullRequestBlueprint,
)

g = Github(GITHUB_ACCESS_TOKEN)
repo = g.get_repo(GITHUB_REPO)


def head(pr: PullRequest) -> HeadBranch:
    return HeadBranch(pr.head.label.split(":")[1])


def base(pr: PullRequest) -> BaseBranch:
    return BaseBranch(pr.base.label.split(":")[1])


def gh_get_pr_title(pr_number: int) -> str:
    pr = repo.get_pull(pr_number)
    return pr.title


def create_gh_pr(
    pr_blueprint: PullRequestBlueprint, silent: bool = False
) -> int | None:
    logger.info(
        f"Creating PR from {pr_blueprint.head} to {pr_blueprint.base} ({pr_blueprint.title})"
    )

    if (
        not silent
        and not q.confirm(f"Create this PR?", default=False, auto_enter=False).ask()
    ):
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

    if not q.confirm(
        f"Create PRs according to above plan?", default=False, auto_enter=False
    ).ask():
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
    user_prs: list[PullRequest] = []
    for pr in prs:
        if pr.user.login == GITHUB_USERNAME:
            user_prs.append(pr)
    return user_prs


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


def select_pr_chain(chains: list[PRChain]) -> PRChain:
    """Prompt the user to select a chain of PRs."""
    if not chains:
        logger.error("No chains found")
        raise ValueError("No chains found")

    # options should look like this:
    # "branch1 <- 653,432,542,435,534 <- branch2"
    # in a way so first_pr.base == branch1 and last_pr.head == branch2
    # and also numbers are pr numbers

    options = []
    for chain in chains:
        first_pr = chain[0]
        last_pr = chain[-1]
        options.append(
            f"{first_pr.base.label.split(':')[1]} <- "
            + ",".join([str(pr.number) for pr in chain])
            + f" <- {last_pr.head.label.split(':')[1]}"
        )

    selection = q.select("Choose a chain:", choices=options).ask()
    logger.info(f"Selected chain: {selection}")
    chain = chains[options.index(selection)] if selection else None

    if not chain:
        logger.error("No chain selected")
        raise ValueError("No chain selected")

    return chain


def select_pr_chain_from_user_opened_prs() -> PRChain:
    """Prompt the user to select a chain of PRs from user's opened PRs."""
    prs = get_user_opened_prs()
    selected_chain = get_pr_chains(prs)
    return select_pr_chain(selected_chain)


def change_pr_title(pr: PullRequest, new_title: str) -> None:
    """Change the title of a PR."""
    pr_number = pr.number
    old_title = pr.title

    if old_title == new_title:
        logger.info(f"PR #{pr_number} has already wanted title. Skipping.")
        return None

    logger.info(
        f"Changing PR #{pr_number} title \nfrom: \n{old_title} \nto: \n{new_title}"
    )
    if not q.confirm(
        f"Change PR #{pr_number} title to: {new_title}?", default=False, auto_enter=True
    ).ask():
        logger.info("Aborting")
        return None

    assert (
        pr.title == old_title
    )  # make sure that the PR title is still the same to avoid race conditions, not sure if it retrieves it again though

    pr.edit(title=new_title)
    logger.info(f"Changed PR #{pr_number} title to: {new_title}")


def ask_for_review(pr: PullRequest) -> None:
    """Ask REVIEWERS to review a PR if they are not under review already."""
    # TODO: remove DRAFT status
    pr_number = pr.number

    # aaa =list(pr.get_reviews())
    # # change draft to non-draft:
    # if pr.draft:
    #     pr.edit(draft=False)
    #     print()

    if pr.draft:
        raise Exception(f"PR {pr_number} is draft")

    if pr.requested_reviewers or pr.get_reviews().totalCount > 0:
        logger.info(f"PR #{pr_number}: already asked for review.")
        return None

    logger.info(f"Asking {REVIEWERS} to review PR #{pr_number}")
    if not q.confirm(
        f"Ask {REVIEWERS} to review PR #{pr_number} ({pr.title})?",
        default=False,
        auto_enter=True,
    ).ask():
        logger.info("Aborting")
        return None

    pr.create_review_request(reviewers=REVIEWERS)
    logger.info(f"Asked {REVIEWERS} to review PR #{pr_number}")


def is_approved(pr: PullRequest) -> bool:
    """Check if a PR is approved."""
    pr_number = pr.number
    reviews = list(pr.get_reviews())
    approved = False
    for review in reviews:
        if review.state == "APPROVED":
            approved = True
            break
    if approved:
        logger.trace(f"PR #{pr_number} is approved")
    else:
        logger.trace(f"PR #{pr_number} is not approved")
    return approved


def pr_is_ready_to_merge(pr: PullRequest, wait: bool = False) -> bool:
    """Check if a PR is ready to merge."""
    pr.update()

    pr_number = pr.number

    if pr.merged:
        raise Exception(f"PR #{pr_number} is already merged")

    if not is_approved(pr):
        raise Exception(f"PR #{pr_number} is not approved")

    if not pr.mergeable:
        raise Exception(f"PR #{pr_number} is not mergeable")

    if pr.draft:
        raise Exception(f"PR #{pr_number} is 'draft'")

    if not pr.rebaseable:
        raise Exception(f"PR #{pr_number} is not rebaseable")

    if pr.state != "open":
        raise Exception(f"PR #{pr_number} is not open: {pr.state=}")

    if pr.created_at < (datetime.datetime.now() - datetime.timedelta(days=30)):
        raise Exception(
            f"PR #{pr_number} was created earlier than 30 days ago: {pr.created_at=}, this is a safety measure to avoid merging old PRs"
        )

    if base(pr) != Branch("main"):
        raise Exception(f"PR #{pr_number} is not based on 'main': {base(pr)=}")

    if not wait:
        if pr.mergeable_state != "clean":
            raise Exception(f"PR #{pr_number} is not clean: {pr.mergeable_state=}")
        else:
            logger.trace(f"PR #{pr_number} is ready to merge")
            return True
    else:
        return pr.mergeable_state == "clean"


def wait_pr_ready_to_merge(pr: PullRequest) -> None:
    """Wait until a PR is ready to merge."""
    pr_number = pr.number
    while True:
        if not pr_is_ready_to_merge(pr, wait=True):
            raise Exception(f"PR #{pr_number} is not ready to merge")
        else:
            if pr.mergeable_state == "clean":
                break
            else:
                logger.info(
                    f"PR #{pr_number} is not ready to merge: {pr.mergeable_state=}. Waiting for it..."
                )
                sleep(10)
    logger.info(f"PR #{pr_number} is ready to merge")


if __name__ == "__main__":
    pass

    # all_prs = get_user_opened_prs()
    # chains = get_pr_chains(all_prs)

    # t1 = gh_get_pr_title(1)
    # print(t1)
    # print()
