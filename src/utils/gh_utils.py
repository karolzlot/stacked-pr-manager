from src.models.types import BaseBranch, HeadBranch, PullRequest


def head(pr: PullRequest) -> HeadBranch:
    return HeadBranch(pr.head.label.split(":")[1])


def base(pr: PullRequest) -> BaseBranch:
    return BaseBranch(pr.base.label.split(":")[1])
