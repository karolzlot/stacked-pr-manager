from src.utils.gh import select_pr_chain_from_user_opened_prs, change_pr_title
from loguru import logger

def rename_prs_chain(template: str, prefix_length: int) -> None:
    chain = select_pr_chain_from_user_opened_prs()
    if not chain:
        logger.info("Aborting, no chains found.")
        return

    for i, pr in enumerate(chain):
        branch_suffix_head = pr.head.label.split(":")[1][prefix_length:] 
        branch_suffix_base = pr.base.label.split(":")[1][prefix_length:] or "m"
        new_pr_title = template.replace("$1", str(i+1)).replace("$2", f"{branch_suffix_head}->{branch_suffix_base}")
        
        change_pr_title(pr, new_pr_title)
        

  

if __name__ == '__main__':

    pass

