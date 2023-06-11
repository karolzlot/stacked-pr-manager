from src.config.logger import logger
from src.utils.gh import select_pr_chain_from_user_opened_prs
from src.utils.pr_chain import merge_base_into_head


def sync_prs_chain() -> None:
    chain = select_pr_chain_from_user_opened_prs()
    if not chain:
        logger.info("Aborting, no chains found.")
        return

    merge_base_into_head(chain)


if __name__ == "__main__":

    sync_prs_chain()
