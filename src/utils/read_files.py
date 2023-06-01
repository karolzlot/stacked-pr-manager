from src.models.types import PRData
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


