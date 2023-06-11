from pathlib import Path

import questionary as q
from ruamel.yaml import YAML

from src.config.logger import logger
from src.models.types import Branch


def load_branches_from_file(file: Path) -> list[Branch]:
    """Load branches list from file (1 branch per line)."""

    with open(file) as f:
        lines = f.readlines()

    branches = []
    for line in lines:
        branches.append(Branch(line.strip()))

    return branches


def find_branches_file() -> Path:
    """Return file from directory, if more than one file, ask user to select one."""
    BRANCHES_DIR = Path("branches/")

    files = list(BRANCHES_DIR.glob("*.txt"))
    if len(files) == 0:
        raise Exception("No files found in branches/ directory.")
    elif len(files) == 1:
        logger.info(f"Using {files[0]}")
        return files[0]
    else:
        options = [file.name for file in files]
        file_name = q.select("Select file with branches:", choices=options).ask()
        logger.info(f"Using {file_name}")
        return BRANCHES_DIR / file_name
