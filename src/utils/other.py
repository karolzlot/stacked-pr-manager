"""create PullRequestBlueprints from a list of Branches"""

from pathlib import Path

import questionary as q
from loguru import logger

from src.config.env_vars import BRANCH_PREFIX
from src.models.types import Branch, PullRequestBlueprint
from src.utils.read_files import load_branches_from_file


def create_pr_blueprints_from_branches(
    branches: list[Branch],
) -> list[PullRequestBlueprint]:
    """Create PullRequestBlueprints from a list of Branches."""
    pr_blueprints = []
    # assume that branches are sorted, so former is the target of the latter

    for i in range(len(branches)):
        if i == 0:
            assert branches[i].startswith(BRANCH_PREFIX) or branches[i] == "main"
            continue
        else:
            assert branches[i].startswith(BRANCH_PREFIX)
            pr_blueprints.append(
                PullRequestBlueprint(
                    head=branches[i],
                    base=branches[i - 1],
                    title=branches[i],
                )
            )

    return pr_blueprints
