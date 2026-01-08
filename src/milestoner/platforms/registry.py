from typing import Type

from .base import Platform
from .bluesky import BlueskyPlatform

# Registry of available platforms
PLATFORMS: dict[str, Type[Platform]] = {
    "bluesky": BlueskyPlatform,
}


def get_platform(name: str) -> Platform:
    """Get a platform instance by name."""
    if name not in PLATFORMS:
        available = ", ".join(PLATFORMS.keys())
        raise ValueError(f"Unknown platform: {name}. Available: {available}")
    return PLATFORMS[name]()


def list_platforms() -> list[str]:
    """List all available platform names."""
    return list(PLATFORMS.keys())
