from src.config.logger import logger
from src.utils.gh import change_pr_title, select_pr_chain_from_user_opened_prs
from src.utils.git import sync_stacked_branches


def sync_prs_chain() -> None:
    chain = select_pr_chain_from_user_opened_prs()
    if not chain:
        logger.info("Aborting, no chains found.")
        return

    sync_stacked_branches(chain)
