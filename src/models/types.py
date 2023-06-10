import re
from typing import NewType, TypedDict
from pydantic import BaseModel
from typing import List
from github.PullRequest import PullRequest


class Commit(str):
    def __new__(cls, commit_hash):
        if not cls._is_valid(commit_hash):
            raise ValueError("Invalid Git commit hash")
        
        return super().__new__(cls, commit_hash)

    @staticmethod
    def _is_valid(commit_hash):
        return bool(re.match("^[0-9a-f]{7,40}$", commit_hash))

class Branch(str):
    pass

class HeadBranch(Branch):
    pass # source

class BaseBranch(Branch):
    pass # target


class PRData(TypedDict):
    """deprecated"""
    branch: Branch
    title: str
    pr_number: int
    target: Branch


class PullRequestBlueprint(BaseModel):
    head: Branch # source
    base: Branch # target
    title: str


class PRChain(List[PullRequest]):
    pass



if __name__ == '__main__':

    pass
