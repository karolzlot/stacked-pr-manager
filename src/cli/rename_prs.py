from src.config.logger import logger
from src.utils.gh import base, change_pr_title, head, select_pr_chain_from_user_opened_prs


def rename_prs_chain(template: str, prefix_length: int) -> None:
    chain = select_pr_chain_from_user_opened_prs()
    if not chain:
        logger.info("Aborting, no chains found.")
        return

    for i, pr in enumerate(chain):
        branch_suffix_head = head(pr)[prefix_length:]
        branch_suffix_base = base(pr)[prefix_length:] or "m"
        new_pr_title = template.replace("$1", str(i + 1)).replace(
            "$2", f"b{branch_suffix_base}<-b{branch_suffix_head}"
        )

        change_pr_title(pr, new_pr_title)


if __name__ == "__main__":
    pass
