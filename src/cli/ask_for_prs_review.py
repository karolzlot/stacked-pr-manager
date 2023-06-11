from src.config.logger import logger
from src.utils.gh import ask_for_review, select_pr_chain_from_user_opened_prs


def ask_for_review_pr_chain() -> None:
    chain = select_pr_chain_from_user_opened_prs()

    for pr in chain:
        ask_for_review(pr)

    logger.warning(
        "Don't forget to remove DRAFT status from PRs. (try selecting many PRs in GUI and then mark all at once as 'open')"
    )


if __name__ == "__main__":
    ask_for_review_pr_chain()

    pass
