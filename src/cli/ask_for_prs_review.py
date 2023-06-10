from src.utils.gh import select_pr_chain_from_user_opened_prs, ask_for_review
from loguru import logger

def ask_for_review_pr_chain() -> None:
    chain = select_pr_chain_from_user_opened_prs()
    if not chain:
        logger.info("Aborting, no chains found.")
        return

    for pr in chain:
        ask_for_review(pr)
    
    logger.warning("Don't forget to remove DRAFT status from PRs. (try selecting many PRs in GUI and then mark all at once as 'open')")

  

if __name__ == '__main__':

    ask_for_review_pr_chain()

    pass
