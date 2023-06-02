from src.utils.read_files import load_branches_from_file, find_branches_file
from src.utils.other import create_pr_blueprints_from_branches
from src.utils.gh import create_gh_prs
from pathlib import Path

def create_prs_from_file() -> None:
    file = find_branches_file()
    branches = load_branches_from_file(file)
    pr_blueprints = create_pr_blueprints_from_branches(branches)
    create_gh_prs(pr_blueprints)

if __name__ == '__main__':
    create_prs_from_file()