from typing import Any

from atproto import Client
from atproto.exceptions import AtProtocolError

from .base import Platform


class BlueskyPlatform(Platform):
    """Bluesky platform implementation using AT Protocol."""

    def __init__(self) -> None:
        self._client: Client | None = None
        self._handle: str | None = None

    @property
    def name(self) -> str:
        return "bluesky"

    @property
    def character_limit(self) -> int:
        return 300

    def authenticate(self, credentials: dict[str, str]) -> bool:
        """Authenticate with Bluesky using handle and app password."""
        handle = credentials.get("handle", "")
        app_password = credentials.get("app_password", "")

        if not handle or not app_password:
            return False

        try:
            self._client = Client()
            self._client.login(handle, app_password)
            self._handle = handle
            return True
        except AtProtocolError:
            self._client = None
            self._handle = None
            return False

    def post(self, content: str) -> dict[str, Any]:
        """Post content to Bluesky."""
        if not self._client:
            return {"success": False, "url": "", "error": "Not authenticated"}

        if len(content) > self.character_limit:
            return {
                "success": False,
                "url": "",
                "error": f"Content exceeds {self.character_limit} character limit",
            }

        try:
            response = self._client.send_post(text=content)
            # Build the URL to the post
            # Format: https://bsky.app/profile/{handle}/post/{rkey}
            uri = response.uri  # at://did:plc:xxx/app.bsky.feed.post/rkey
            rkey = uri.split("/")[-1]
            url = f"https://bsky.app/profile/{self._handle}/post/{rkey}"
            return {"success": True, "url": url, "error": ""}
        except AtProtocolError as e:
            return {"success": False, "url": "", "error": str(e)}

    def get_credential_schema(self) -> dict[str, str]:
        return {
            "handle": "Your Bluesky handle (e.g., yourname.bsky.social)",
            "app_password": "App password from bsky.app/settings/app-passwords",
        }
