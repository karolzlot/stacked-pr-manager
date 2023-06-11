from src.utils.gh import select_pr_chain_from_user_opened_prs, change_pr_title
from src.utils.git import sync_stacked_branches
from src.config.logger import logger




def sync_prs_chain() -> None:
    chain = select_pr_chain_from_user_opened_prs()
    if not chain:
        logger.info("Aborting, no chains found.")
        return
    
    sync_stacked_branches(chain)

