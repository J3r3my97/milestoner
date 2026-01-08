import json
import os
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".milestoner"
CONFIG_FILE = CONFIG_DIR / "config.json"
POST_HISTORY_FILE = CONFIG_DIR / "post-history.json"


def _ensure_config_dir() -> None:
    """Ensure config directory exists with proper permissions."""
    CONFIG_DIR.mkdir(mode=0o700, exist_ok=True)


def _read_json(path: Path) -> dict[str, Any]:
    """Read a JSON file, returning empty dict if not found."""
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _write_json(path: Path, data: dict[str, Any]) -> None:
    """Write data to JSON file with restricted permissions."""
    _ensure_config_dir()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(path, 0o600)


def get_config() -> dict[str, Any]:
    """Get the full configuration."""
    return _read_json(CONFIG_FILE)


def save_config(config: dict[str, Any]) -> None:
    """Save the full configuration."""
    _write_json(CONFIG_FILE, config)


def get_platform_credentials(platform: str) -> dict[str, str] | None:
    """Get credentials for a specific platform."""
    config = get_config()
    return config.get("platforms", {}).get(platform)


def save_platform_credentials(platform: str, credentials: dict[str, str]) -> None:
    """Save credentials for a specific platform."""
    config = get_config()
    if "platforms" not in config:
        config["platforms"] = {}
    config["platforms"][platform] = credentials
    save_config(config)


def get_default_platform() -> str:
    """Get the default platform name."""
    config = get_config()
    return config.get("defaults", {}).get("platform", "bluesky")


def set_default_platform(platform: str) -> None:
    """Set the default platform."""
    config = get_config()
    if "defaults" not in config:
        config["defaults"] = {}
    config["defaults"]["platform"] = platform
    save_config(config)


def get_post_history() -> list[dict[str, Any]]:
    """Get the history of posts made through Milestoner."""
    data = _read_json(POST_HISTORY_FILE)
    return data.get("posts", [])


def add_post_to_history(post: dict[str, Any]) -> None:
    """Add a post to the history."""
    data = _read_json(POST_HISTORY_FILE)
    if "posts" not in data:
        data["posts"] = []
    data["posts"].append(post)
    _write_json(POST_HISTORY_FILE, data)
