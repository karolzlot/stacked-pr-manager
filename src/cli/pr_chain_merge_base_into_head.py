from src.config.logger import logger
from src.utils.gh import select_pr_chain_from_user_opened_prs
from src.utils.pr_chain import merge_base_into_head


def pr_chain_merge_base_into_head() -> None:
    chain = select_pr_chain_from_user_opened_prs()
    if not chain:
        logger.info("Aborting, no chains found.")
        return

    merge_base_into_head(chain)


if __name__ == "__main__":

    pr_chain_merge_base_into_head()
