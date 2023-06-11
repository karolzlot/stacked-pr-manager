import re
from typing import List, TypedDict

from github.PullRequest import PullRequest
from pydantic import BaseModel

from src.models.types.branch import *


class Commit(str):
    def __new__(cls, commit_hash):
        if not cls._is_valid(commit_hash):
            raise ValueError("Invalid Git commit hash")

        return super().__new__(cls, commit_hash)

    @staticmethod
    def _is_valid(commit_hash) -> bool:
        return bool(re.match(r"^[0-9a-f]{40}$", commit_hash))


class PRData(TypedDict):
    """deprecated"""

    branch: Branch
    title: str
    pr_number: int
    target: Branch


class PullRequestBlueprint(BaseModel):
    head: Branch  # source
    base: Branch  # target
    title: str


class PRChain(list[PullRequest]):
    pass


if __name__ == "__main__":
    pass
