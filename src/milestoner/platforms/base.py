from abc import ABC, abstractmethod
from typing import Any


class Platform(ABC):
    """Abstract base class for social platforms."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Platform identifier (e.g., 'bluesky')."""
        pass

    @property
    @abstractmethod
    def character_limit(self) -> int:
        """Maximum characters per post."""
        pass

    @abstractmethod
    def authenticate(self, credentials: dict[str, str]) -> bool:
        """Validate and store credentials. Returns True if successful."""
        pass

    @abstractmethod
    def post(self, content: str) -> dict[str, Any]:
        """
        Post content to the platform.

        Returns:
            dict with keys:
                - success (bool): Whether the post was successful
                - url (str): URL to the published post (if successful)
                - error (str): Error message (if failed)
        """
        pass

    @abstractmethod
    def get_credential_schema(self) -> dict[str, str]:
        """
        Returns the required credential fields for this platform.

        Example: {"handle": "Your Bluesky handle", "app_password": "App password from settings"}
        """
        pass
