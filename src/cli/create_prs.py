from src.utils.gh import create_gh_prs
from src.utils.other import create_pr_blueprints_from_branches
from src.utils.read_files import find_branches_file, load_branches_from_file


def create_prs_from_file() -> None:
    file = find_branches_file()
    branches = load_branches_from_file(file)
    pr_blueprints = create_pr_blueprints_from_branches(branches)
    create_gh_prs(pr_blueprints)


if __name__ == "__main__":
    create_prs_from_file()
