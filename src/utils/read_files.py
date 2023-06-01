from src.models.types import PRData, Branch
from pathlib import Path
from ruamel.yaml import YAML



def read_prs_config_file() -> list[PRData]:
    file_path = Path('prs.yaml')
    with open(file_path, 'r') as file:
        yaml = YAML(typ='safe')
        prs_data: list[dict] = yaml.load(file)

    pull_requests_list = []
    for entry in prs_data:
        pull_request = PRData(
            branch=entry['branch'],
            title=entry['title'],
            pr_number=entry['pr_number'],
            target=entry['target']
        )
        pull_requests_list.append(pull_request)

    return pull_requests_list


def load_branches_from_file(file: Path) -> list[Branch]:
    """Load branches list from file (1 branch per line)."""

    with open(file, "r") as f:
        lines = f.readlines()

    branches = []
    for line in lines:
        branches.append(Branch(line.strip()))

    return branches


        

