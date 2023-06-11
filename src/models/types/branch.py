import re


class Branch(str):
    """Branch is a subclass of str that represents a Git branch name."""

    def __new__(cls, name):
        """Create and return a new Branch."""
        if not cls.is_valid(name):
            raise ValueError(f"'{name}' is not a valid Git branch name")

        return str.__new__(cls, name)

    @staticmethod
    def is_valid(name) -> bool:
        """Return True -> bool if name is a valid Git branch name, False otherwise."""
        min_len = 4
        max_len = 30

        # Ensure length is within acceptable bounds
        if len(name) < min_len or len(name) > max_len:
            return False

        # Check if there is a special character
        if re.match(r"^[\w\-/\.]+$", name) is None:
            return False

        # Can't start or end with a slash
        if name.startswith("/") or name.endswith("/"):
            return False

        # No consecutive slashes
        if "//" in name:
            return False

        # No special characters
        if (
            "~" in name
            or "^" in name
            or ":" in name
            or " " in name
            or "?" in name
            or "[" in name
            or "*" in name
            or "\\" in name
        ):
            return False

        # No @{ or ..
        if "@{" in name or ".." in name:
            return False

        # No dot
        if "." in name:
            return False
        return True


class HeadBranch(Branch):
    """Head branch == source branch of a PR."""

    pass


class BaseBranch(Branch):
    """Base branch == target branch of a PR."""

    pass
