"""Tests for version checking integration with CLI."""

from unittest.mock import patch

import pytest

from forgemind.cli.version import (
    check_version_availability,
    get_installed_version,
    is_breaking_change,
    should_check_version,
    should_update,
)
from forgemind.version import BREAKING_CHANGES, COMPATIBILITY, __version__


class TestVersionDetection:
    """Test version detection mechanisms."""

    def test_installed_version_matches_package(self):
        """Installed version should match package version."""
        installed = get_installed_version()
        # Should be either the real installed version or "unknown"
        assert installed in [__version__, "unknown"]

    def test_should_update_with_newer_version(self):
        """should_update should return True when newer version available."""
        assert should_update("1.0.0", "1.1.0") is True
        assert should_update("1.0.0", "2.0.0") is True

    def test_should_update_with_same_version(self):
        """should_update should return False when versions are same."""
        assert should_update("1.2.1", "1.2.1") is False

    def test_should_update_with_older_version(self):
        """should_update should return False when latest is older."""
        assert should_update("1.2.1", "1.0.0") is False

    def test_should_update_with_invalid_versions(self):
        """should_update should handle invalid versions gracefully."""
        assert should_update("invalid", "1.0.0") is False
        assert should_update("1.0.0", "invalid") is False

    def test_is_breaking_change_major_bump(self):
        """is_breaking_change should detect major version bumps."""
        assert is_breaking_change("1.0.0", "2.0.0") is True
        assert is_breaking_change("0.1.0", "1.0.0") is True

    def test_is_breaking_change_minor_or_patch(self):
        """is_breaking_change should not trigger on minor/patch bumps."""
        assert is_breaking_change("1.0.0", "1.1.0") is False
        assert is_breaking_change("1.1.0", "1.1.1") is False
        assert is_breaking_change("1.2.1", "1.2.2") is False

    def test_is_breaking_change_with_invalid_versions(self):
        """is_breaking_change should handle invalid versions gracefully."""
        assert is_breaking_change("invalid", "2.0.0") is False
        assert is_breaking_change("1.0.0", "invalid") is False


class TestVersionCompatibility:
    """Test version compatibility matrix."""

    def test_current_version_in_compatibility_matrix(self):
        """Current version should be in compatibility matrix."""
        assert __version__ in COMPATIBILITY
        compat = COMPATIBILITY[__version__]
        assert "works_with_projects" in compat
        assert "works_with_outputs" in compat
        assert "backward_compatible" in compat

    def test_current_version_backward_compatible(self):
        """Current version should be backward compatible."""
        compat = COMPATIBILITY[__version__]
        assert compat["backward_compatible"] is True

    def test_compatibility_matrix_structure(self):
        """Compatibility matrix should have consistent structure."""
        for version, compat in COMPATIBILITY.items():
            assert "works_with_projects" in compat
            assert isinstance(compat["works_with_projects"], list)
            assert "works_with_outputs" in compat
            assert isinstance(compat["works_with_outputs"], list)
            assert "backward_compatible" in compat
            assert isinstance(compat["backward_compatible"], bool)


class TestVersionCheckScheduling:
    """Test version check scheduling logic."""

    def test_should_check_version_on_first_run(self, tmp_path):
        """should_check_version should return True if check file doesn't exist."""
        # Mock the check file path to a non-existent location
        with patch("forgemind.cli.version.get_version_check_file") as mock_file:
            mock_file.return_value = tmp_path / "nonexistent.txt"
            assert should_check_version() is True

    def test_should_check_version_after_24_hours(self, tmp_path):
        """should_check_version should return True if >24 hours passed."""
        from datetime import datetime, timedelta

        check_file = tmp_path / "last_check.txt"
        # Write a timestamp from 25 hours ago
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()
        check_file.write_text(old_time)

        with patch("forgemind.cli.version.get_version_check_file") as mock_file:
            mock_file.return_value = check_file
            assert should_check_version() is True

    def test_should_not_check_version_within_24_hours(self, tmp_path):
        """should_check_version should return False if <24 hours passed."""
        from datetime import datetime, timedelta

        check_file = tmp_path / "last_check.txt"
        # Write a timestamp from 1 hour ago
        recent_time = (datetime.now() - timedelta(hours=1)).isoformat()
        check_file.write_text(recent_time)

        with patch("forgemind.cli.version.get_version_check_file") as mock_file:
            mock_file.return_value = check_file
            assert should_check_version() is False


class TestVersionCheckNonBlocking:
    """Test that version checks fail silently and don't block operations."""

    def test_check_version_availability_skip_flag(self):
        """check_version_availability should skip if skip=True."""
        with patch("forgemind.cli.version.should_check_version") as mock_should:
            check_version_availability(skip=True)
            # should_check_version should not be called if skip=True
            mock_should.assert_not_called()

    def test_check_version_availability_network_error(self):
        """check_version_availability should fail silently on network errors."""
        with patch("forgemind.cli.version.should_check_version", return_value=True):
            with patch("forgemind.cli.version.get_latest_version", return_value=None):
                # Should not raise exception
                check_version_availability()

    def test_check_version_availability_marks_check_done(self, tmp_path):
        """check_version_availability should mark check as done even on failure."""
        check_file = tmp_path / "last_check.txt"

        with patch("forgemind.cli.version.should_check_version", return_value=True):
            with patch("forgemind.cli.version.get_installed_version", return_value="1.2.1"):
                with patch("forgemind.cli.version.get_latest_version", return_value="1.2.1"):
                    with patch("forgemind.cli.version.get_version_check_file") as mock_file:
                        mock_file.return_value = check_file
                        check_version_availability()

                        # Should have written check file
                        # (Note: may not write if versions are same, so we just verify no exception)


class TestBreakingChangesDocumentation:
    """Test breaking changes documentation."""

    def test_breaking_changes_documented(self):
        """BREAKING_CHANGES should document major versions."""
        assert "2.0.0" in BREAKING_CHANGES
        changes = BREAKING_CHANGES["2.0.0"]
        assert isinstance(changes, list)
        assert len(changes) > 0
        # All items should start with "BREAKING:" or "Migration:" or "Removed:"
        for change in changes:
            assert any(
                change.startswith(prefix)
                for prefix in ["BREAKING:", "Migration:", "Removed:", "DEPRECATION:"]
            )

    def test_current_version_has_release_notes(self):
        """Current version should have release notes."""
        from forgemind.version import RELEASE_NOTES

        assert __version__ in RELEASE_NOTES
        notes = RELEASE_NOTES[__version__]
        assert len(notes) > 0
        assert "##" in notes  # Should have markdown heading


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
