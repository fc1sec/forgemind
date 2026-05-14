"""Version checking and update notifications."""

import json
import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def get_installed_version() -> str:
    """Get currently installed ForgeMind version."""
    try:
        result = subprocess.run(
            ["pip", "show", "forgemind"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        for line in result.stdout.split("\n"):
            if line.startswith("Version:"):
                return line.split(": ", 1)[1].strip()
    except Exception:
        pass
    return "unknown"


def get_latest_version() -> Optional[str]:
    """Check latest version available on PyPI."""
    try:
        import urllib.request

        with urllib.request.urlopen(
            "https://pypi.org/pypi/forgemind/json", timeout=5
        ) as resp:
            data = json.loads(resp.read())
            return data["info"]["version"]
    except Exception:
        return None


def should_update(current: str, latest: str) -> bool:
    """Check if update is available and recommended."""
    if not latest or current == "unknown":
        return False

    try:
        from packaging import version

        return version.parse(latest) > version.parse(current)
    except Exception:
        return False


def is_breaking_change(from_version: str, to_version: str) -> bool:
    """Check if update includes breaking changes (major version bump)."""
    try:
        from packaging import version

        from_major = version.parse(from_version).major
        to_major = version.parse(to_version).major
        return to_major > from_major
    except Exception:
        return False


def get_version_check_file() -> Path:
    """Get path to version check timestamp file."""
    check_dir = Path.home() / ".forgemind" / "version_checks"
    check_dir.mkdir(parents=True, exist_ok=True)
    return check_dir / "last_check.txt"


def should_check_version() -> bool:
    """Check if enough time has passed since last version check (daily)."""
    check_file = get_version_check_file()

    if not check_file.exists():
        return True

    try:
        from datetime import datetime, timedelta

        last_check = datetime.fromisoformat(check_file.read_text().strip())
        if datetime.now() - last_check > timedelta(days=1):
            return True
    except Exception:
        pass

    return False


def mark_version_check_done() -> None:
    """Mark that version check was performed."""
    try:
        from datetime import datetime

        check_file = get_version_check_file()
        check_file.write_text(datetime.now().isoformat())
    except Exception:
        pass


def notify_update_available(current: str, latest: str) -> None:
    """Display notification about available update."""
    breaking = is_breaking_change(current, latest)

    if breaking:
        console.print(
            f"""
[bold yellow]⚠️  Major Update Available: v{current} → v{latest}[/bold yellow]

This is a [bold]MAJOR version update[/bold] with breaking changes.

[bold]Before updating:[/bold]
  1. Backup your [cyan].forgemind/[/cyan] directory
  2. Read [cyan]BREAKING_CHANGES.md[/cyan]
  3. Test in non-critical project first
  4. Update: [cyan]pip install --upgrade forgemind[/cyan]

[dim]ℹ️  See UPDATES_AND_SAFETY.md for safe upgrade procedures[/dim]
[dim]💾 Don't worry: Your projects are safe. See COMPATIBILITY_MATRIX.md[/dim]
        """.strip()
        )
    else:
        console.print(
            f"""
[bold green]✓ Update available: v{current} → v{latest}[/bold green]

[dim]Backward compatible. Safe to update anytime.[/dim]
Update: [cyan]pip install --upgrade forgemind[/cyan]
        """.strip()
        )


def check_version_availability(skip: bool = False) -> None:
    """Check if new version is available and notify user if so."""
    if skip or not should_check_version():
        return

    try:
        current = get_installed_version()
        latest = get_latest_version()

        if should_update(current, latest):
            notify_update_available(current, latest)

        mark_version_check_done()
    except Exception:
        # Fail silently - version check shouldn't block normal operation
        pass
