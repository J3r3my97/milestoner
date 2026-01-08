from typing import Any

from ..config.store import get_config, save_platform_credentials, set_default_platform
from ..platforms.registry import get_platform, list_platforms


def configure(
    platform: str,
    set_default: bool = True,
    **credentials: str,
) -> dict[str, Any]:
    """
    Configure credentials for a platform.

    Args:
        platform: Platform to configure (e.g., "bluesky")
        set_default: Whether to set this as the default platform
        **credentials: Platform-specific credentials (e.g., handle, app_password)

    Returns:
        Success/failure status with validation result
    """
    # Validate platform
    if platform not in list_platforms():
        return {
            "success": False,
            "error": f"Unknown platform: {platform}. Available: {', '.join(list_platforms())}",
        }

    # Get platform instance
    platform_instance = get_platform(platform)
    required_schema = platform_instance.get_credential_schema()

    # Check required credentials
    missing = [key for key in required_schema if key not in credentials]
    if missing:
        return {
            "success": False,
            "error": f"Missing required credentials: {', '.join(missing)}",
            "required": required_schema,
        }

    # Validate credentials by attempting to authenticate
    if not platform_instance.authenticate(credentials):
        return {
            "success": False,
            "error": "Authentication failed. Please check your credentials.",
        }

    # Save credentials
    save_platform_credentials(platform, credentials)

    # Set as default if requested
    if set_default:
        set_default_platform(platform)

    return {
        "success": True,
        "message": f"Successfully configured {platform}.",
        "is_default": set_default,
    }


def get_configuration_status() -> dict[str, Any]:
    """Get the current configuration status for all platforms."""
    config = get_config()
    platforms_config = config.get("platforms", {})
    default_platform = config.get("defaults", {}).get("platform", "bluesky")

    status: dict[str, Any] = {
        "default_platform": default_platform,
        "platforms": {},
    }

    for platform_name in list_platforms():
        platform_instance = get_platform(platform_name)
        creds = platforms_config.get(platform_name, {})

        status["platforms"][platform_name] = {
            "configured": bool(creds),
            "is_default": platform_name == default_platform,
            "required_credentials": list(platform_instance.get_credential_schema().keys()),
        }

    return status
