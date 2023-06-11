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
        """Return True -> bool if name is a valid Git branch name, False otherwise.
        """
        min_len = 4
        max_len = 30
        if len(name) < min_len or len(name) > max_len:  # Ensure length is within acceptable bounds
            return False
        if re.match(r'^[\w\.-]+$', name) is None:  # Check if there is a special character
            return False
        if name.startswith("/") or name.endswith("/"):  # Can't start or end with a slash
            return False
        if "//" in name:  # No consecutive slashes
            return False
        if "~" in name or "^" in name or ":" in name or " " in name or "?" in name or "[" in name or "*" in name or "\\" in name:  # No special characters
            return False
        if "@{" in name or ".." in name:  # No @{ or ..
            return False
        if "." in name:  # No dot
            return False
        return True


class HeadBranch(Branch):
    """Head branch == source branch of a PR."""
    pass

class BaseBranch(Branch):
    """Base branch == target branch of a PR."""
    pass
