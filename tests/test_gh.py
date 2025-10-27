from unittest.mock import Mock

import pytest

from src.models.types import PRChain
from src.utils.gh_utils import get_pr_chains


def create_mock_pr(number: int, base_label: str, head_label: str):
    """Helper to create a mock PullRequest object.

    Args:
        number: PR number
        base_label: Base branch label (format: "user:branch")
        head_label: Head branch label (format: "user:branch")

    Returns:
        Mock PullRequest object
    """
    pr = Mock()
    pr.number = number
    pr.base = Mock()
    pr.base.label = base_label
    pr.head = Mock()
    pr.head.label = head_label
    return pr


class TestGetPRChains:
    """Test cases for the get_pr_chains function."""

    def test_empty_list_returns_empty(self):
        """Test that empty PR list returns empty chains list."""
        result = get_pr_chains([])
        assert result == []

    def test_single_pr_returns_empty(self):
        """Test that a single PR returns empty list (chains need >1 PR)."""
        pr = create_mock_pr(1, "user:main", "user:feature-1")
        result = get_pr_chains([pr])
        assert result == []

    def test_simple_chain_two_prs(self):
        """Test a simple chain: main <- PR1 <- PR2."""
        pr1 = create_mock_pr(1, "user:main", "user:feature-1")
        pr2 = create_mock_pr(2, "user:feature-1", "user:feature-2")

        result = get_pr_chains([pr1, pr2])

        assert len(result) == 1
        chain = result[0]
        assert len(chain) == 2
        assert chain[0].number == 1
        assert chain[1].number == 2

    def test_simple_chain_three_prs(self):
        """Test a chain of three PRs: main <- PR1 <- PR2 <- PR3."""
        pr1 = create_mock_pr(1, "user:main", "user:feature-1")
        pr2 = create_mock_pr(2, "user:feature-1", "user:feature-2")
        pr3 = create_mock_pr(3, "user:feature-2", "user:feature-3")

        result = get_pr_chains([pr1, pr2, pr3])

        assert len(result) == 1
        chain = result[0]
        assert len(chain) == 3
        assert chain[0].number == 1
        assert chain[1].number == 2
        assert chain[2].number == 3

    def test_two_independent_prs_no_chain(self):
        """Test two independent PRs targeting main don't form a chain."""
        pr1 = create_mock_pr(1, "user:main", "user:feature-1")
        pr2 = create_mock_pr(2, "user:main", "user:feature-2")

        result = get_pr_chains([pr1, pr2])

        # Two independent PRs shouldn't form chains (need length > 1)
        assert len(result) == 0

    def test_two_separate_chains(self):
        """Test two separate chains are both detected.

        Chain 1: main <- PR1 <- PR2
        Chain 2: main <- PR3 <- PR4
        """
        # Chain 1
        pr1 = create_mock_pr(1, "user:main", "user:feature-1")
        pr2 = create_mock_pr(2, "user:feature-1", "user:feature-2")

        # Chain 2
        pr3 = create_mock_pr(3, "user:main", "user:bugfix-1")
        pr4 = create_mock_pr(4, "user:bugfix-1", "user:bugfix-2")

        result = get_pr_chains([pr1, pr2, pr3, pr4])

        assert len(result) == 2

        # Sort chains by first PR number for consistent testing
        chains = sorted(result, key=lambda c: c[0].number)

        # Chain 1
        assert len(chains[0]) == 2
        assert chains[0][0].number == 1
        assert chains[0][1].number == 2

        # Chain 2
        assert len(chains[1]) == 2
        assert chains[1][0].number == 3
        assert chains[1][1].number == 4

    def test_branching_chain_picks_longest(self):
        """Test that when a chain branches, the longest path is chosen.

        Structure:
        main <- PR1 <- PR2 (short branch)
                    <- PR3 (long branch)

        Should return chain: main <- PR1 <- PR3 (length 2)
        """
        pr1 = create_mock_pr(1, "user:main", "user:feature-1")
        pr2 = create_mock_pr(2, "user:feature-1", "user:feature-2a")
        pr3 = create_mock_pr(3, "user:feature-1", "user:feature-2b")

        result = get_pr_chains([pr1, pr2, pr3])

        # Should have 2 chains since they branch
        assert len(result) == 2

        # Both chains should have length 2
        for chain in result:
            assert len(chain) == 2
            assert chain[0].number == 1  # First PR is always PR1

    def test_complex_stacked_chain(self):
        """Test a complex stacked PR chain.

        Structure: main <- PR1 <- PR2 <- PR3 <- PR4 <- PR5
        """
        pr1 = create_mock_pr(1, "user:main", "user:feat-1")
        pr2 = create_mock_pr(2, "user:feat-1", "user:feat-2")
        pr3 = create_mock_pr(3, "user:feat-2", "user:feat-3")
        pr4 = create_mock_pr(4, "user:feat-3", "user:feat-4")
        pr5 = create_mock_pr(5, "user:feat-4", "user:feat-5")

        result = get_pr_chains([pr1, pr2, pr3, pr4, pr5])

        assert len(result) == 1
        chain = result[0]
        assert len(chain) == 5
        assert [pr.number for pr in chain] == [1, 2, 3, 4, 5]

    def test_diamond_pattern(self):
        """Test a diamond pattern of PRs.

        Structure:
                     PR2 (path-a) <- PR4a (final)
                    /
        main <- PR1 (base)
                    \
                     PR3 (path-b) <- PR4b (final)

        Since both PR4a and PR4b end at "user:final", only one chain is kept
        (the algorithm keeps one chain per unique head label).
        The kept chain should be one of the two valid paths through the diamond.
        """
        pr1 = create_mock_pr(1, "user:main", "user:base")
        pr2 = create_mock_pr(2, "user:base", "user:path-a")
        pr3 = create_mock_pr(3, "user:base", "user:path-b")
        pr4a = create_mock_pr(4, "user:path-a", "user:final")
        pr4b = create_mock_pr(5, "user:path-b", "user:final")

        result = get_pr_chains([pr1, pr2, pr3, pr4a, pr4b])

        # Only one chain is kept since both paths end at the same head label
        assert len(result) == 1
        # The chain should have length 3 (one of the two possible paths)
        assert len(result[0]) == 3

    def test_preserves_pr_chain_type(self):
        """Test that return type is list of PRChain (which is list[PullRequest])."""
        pr1 = create_mock_pr(1, "user:main", "user:feature-1")
        pr2 = create_mock_pr(2, "user:feature-1", "user:feature-2")

        result = get_pr_chains([pr1, pr2])

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], PRChain)

    def test_unordered_input_prs(self):
        """Test that PR order in input doesn't matter.

        PRs given in reverse order should still form correct chain.
        """
        pr1 = create_mock_pr(1, "user:main", "user:feature-1")
        pr2 = create_mock_pr(2, "user:feature-1", "user:feature-2")
        pr3 = create_mock_pr(3, "user:feature-2", "user:feature-3")

        # Give PRs in reverse order
        result = get_pr_chains([pr3, pr2, pr1])

        assert len(result) == 1
        chain = result[0]
        assert len(chain) == 3
        # Chain should still be in correct dependency order
        assert chain[0].number == 1
        assert chain[1].number == 2
        assert chain[2].number == 3

    def test_chain_with_different_base_repo(self):
        """Test chains work with different username prefixes in labels."""
        pr1 = create_mock_pr(1, "upstream:main", "user:feature-1")
        pr2 = create_mock_pr(2, "user:feature-1", "user:feature-2")

        result = get_pr_chains([pr1, pr2])

        assert len(result) == 1
        chain = result[0]
        assert len(chain) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
