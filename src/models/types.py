import re
from typing import NewType, TypedDict



class Commit(str):
    def __new__(cls, commit_hash):
        if not cls._is_valid(commit_hash):
            raise ValueError("Invalid Git commit hash")
        
        return super().__new__(cls, commit_hash)

    @staticmethod
    def _is_valid(commit_hash):
        return bool(re.match("^[0-9a-f]{7,40}$", commit_hash))



Branch = NewType('Branch', str)

class PRData(TypedDict):
    branch: Branch
    title: str
    pr_number: int
    target: Branch
