from src.config.logger import logger
from src.utils.gh import select_pr_chain_from_user_opened_prs
from src.utils.pr_chain import push


def pr_chain_push() -> None:
    chain = select_pr_chain_from_user_opened_prs()

    push(chain)


if __name__ == "__main__":

    pr_chain_push()
