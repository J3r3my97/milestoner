from datetime import datetime
from typing import Any

from ..config.store import (
    add_post_to_history,
    get_default_platform,
    get_platform_credentials,
)
from ..platforms.registry import get_platform, list_platforms


def post_update(
    content: str,
    platform: str | None = None,
) -> dict[str, Any]:
    """
    Post content to a social platform.

    Args:
        content: The content to post
        platform: Target platform (defaults to configured default)

    Returns:
        Success/failure status with link to published post
    """
    # Determine platform
    if platform is None:
        platform = get_default_platform()

    # Validate platform
    if platform not in list_platforms():
        return {
            "success": False,
            "error": f"Unknown platform: {platform}. Available: {', '.join(list_platforms())}",
        }

    # Get credentials
    credentials = get_platform_credentials(platform)
    if not credentials:
        return {
            "success": False,
            "error": f"Platform '{platform}' is not configured. Use the configure tool first.",
        }

    # Get platform instance and authenticate
    platform_instance = get_platform(platform)

    if not platform_instance.authenticate(credentials):
        return {
            "success": False,
            "error": "Authentication failed. Please reconfigure your credentials.",
        }

    # Post the content
    result = platform_instance.post(content)

    # Save to history if successful
    if result["success"]:
        add_post_to_history(
            {
                "platform": platform,
                "content": content,
                "url": result["url"],
                "posted_at": datetime.now().isoformat(),
            }
        )

    return result
