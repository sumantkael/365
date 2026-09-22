import sys
import urllib.request
import json
from pathlib import Path

# GitHub repo info for version checking
REPO_OWNER = "sumantkael"
REPO_NAME = "Date"

# Direct raw version check URL & releases web page
VERSION_RAW_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/VERSION"
RELEASES_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases"

def get_current_version() -> str:
    """Reads local version from VERSION file or bundled default."""
    try:
        base_dir = Path(__file__).parent
        v_file = base_dir / "VERSION"
        if not v_file.exists():
            v_file = Path(sys.executable).parent / "VERSION"
        if v_file.exists():
            with open(v_file, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception:
        pass
    return "1.2.0"

def _parse_version_tuple(v_str: str) -> tuple:
    """Converts '1.2.0' to (1, 2, 0) for reliable comparison."""
    try:
        cleaned = v_str.strip().lstrip("vV")
        return tuple(int(x) for x in cleaned.split(".") if x.isdigit())
    except Exception:
        return (0, 0, 0)

def check_for_update(timeout: float = 3.0) -> dict | None:
    """
    Silently checks if a newer version is available on GitHub.
    Returns dict with update info if newer version exists, else None.
    Does not throw exceptions or freeze the caller.
    """
    try:
        headers = {"User-Agent": "365-Desktop-App"}
        req = urllib.request.Request(VERSION_RAW_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            remote_ver_str = resp.read().decode("utf-8").strip()

        current_ver_str = get_current_version()
        remote_tuple = _parse_version_tuple(remote_ver_str)
        current_tuple = _parse_version_tuple(current_ver_str)

        if remote_tuple > current_tuple:
            return {
                "update_available": True,
                "current_version": current_ver_str,
                "latest_version": remote_ver_str,
                "download_url": RELEASES_URL
            }
    except Exception:
        pass

    return None
