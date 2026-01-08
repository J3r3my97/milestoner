"""Scheduled post management."""

from datetime import datetime
from typing import Any

from ..config.store import CONFIG_DIR, _ensure_config_dir, _read_json, _write_json
from ..platforms.registry import get_platform, list_platforms
from ..scheduling import get_optimal_times

SCHEDULED_POSTS_FILE = CONFIG_DIR / "scheduled-posts.json"


def get_scheduled_posts() -> list[dict[str, Any]]:
    """Get all scheduled posts."""
    data = _read_json(SCHEDULED_POSTS_FILE)
    posts = data.get("posts", [])
    # Filter out past posts that weren't posted
    now = datetime.now().isoformat()
    return [p for p in posts if p.get("scheduled_for", "") >= now or p.get("status") == "posted"]


def schedule_post(
    content: str,
    scheduled_for: str | None = None,
    platform: str | None = None,
    use_optimal_time: bool = False,
) -> dict[str, Any]:
    """
    Schedule a post for later.

    Args:
        content: The content to post
        scheduled_for: ISO datetime string for when to post (e.g., "2025-01-15T10:00:00")
        platform: Target platform (defaults to configured default)
        use_optimal_time: If True, schedule for next optimal time

    Returns:
        Scheduled post details
    """
    # Determine platform
    if platform is None:
        from ..config.store import get_default_platform

        platform = get_default_platform()

    # Validate platform
    if platform not in list_platforms():
        return {
            "success": False,
            "error": f"Unknown platform: {platform}. Available: {', '.join(list_platforms())}",
        }

    # Get platform for character limit check
    platform_instance = get_platform(platform)
    if len(content) > platform_instance.character_limit:
        return {
            "success": False,
            "error": f"Content exceeds {platform_instance.character_limit} character limit",
        }

    # Determine scheduled time
    if use_optimal_time or scheduled_for is None:
        optimal = get_optimal_times()
        if optimal["recommendations"]:
            scheduled_for = optimal["recommendations"][0]["datetime"]
        else:
            return {
                "success": False,
                "error": "No optimal times available. Please specify a time.",
            }
    else:
        # Validate the provided datetime
        try:
            datetime.fromisoformat(scheduled_for.replace("Z", "+00:00"))
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid datetime format: {scheduled_for}. Use ISO format.",
            }

    # Create scheduled post
    post_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    scheduled_post = {
        "id": post_id,
        "content": content,
        "platform": platform,
        "scheduled_for": scheduled_for,
        "created_at": datetime.now().isoformat(),
        "status": "scheduled",
    }

    # Save to file
    _ensure_config_dir()
    data = _read_json(SCHEDULED_POSTS_FILE)
    if "posts" not in data:
        data["posts"] = []
    data["posts"].append(scheduled_post)
    _write_json(SCHEDULED_POSTS_FILE, data)

    return {
        "success": True,
        "post": scheduled_post,
        "message": f"Post scheduled for {scheduled_for}",
    }


def list_scheduled_posts() -> dict[str, Any]:
    """List all pending scheduled posts."""
    posts = get_scheduled_posts()
    pending = [p for p in posts if p.get("status") == "scheduled"]
    optimal = get_optimal_times()

    return {
        "pending_posts": pending,
        "count": len(pending),
        "next_optimal_times": optimal["recommendations"][:3],
    }


def cancel_scheduled_post(post_id: str) -> dict[str, Any]:
    """Cancel a scheduled post."""
    data = _read_json(SCHEDULED_POSTS_FILE)
    posts = data.get("posts", [])

    for post in posts:
        if post.get("id") == post_id:
            post["status"] = "cancelled"
            _write_json(SCHEDULED_POSTS_FILE, data)
            return {"success": True, "message": f"Post {post_id} cancelled"}

    return {"success": False, "error": f"Post {post_id} not found"}


def get_due_posts() -> list[dict[str, Any]]:
    """Get posts that are due to be posted now."""
    data = _read_json(SCHEDULED_POSTS_FILE)
    posts = data.get("posts", [])
    now = datetime.now().isoformat()

    due = []
    for post in posts:
        if post.get("status") == "scheduled" and post.get("scheduled_for", "") <= now:
            due.append(post)

    return due


def mark_post_as_posted(post_id: str, url: str) -> dict[str, Any]:
    """Mark a scheduled post as posted."""
    data = _read_json(SCHEDULED_POSTS_FILE)
    posts = data.get("posts", [])

    for post in posts:
        if post.get("id") == post_id:
            post["status"] = "posted"
            post["posted_at"] = datetime.now().isoformat()
            post["url"] = url
            _write_json(SCHEDULED_POSTS_FILE, data)
            return {"success": True}

    return {"success": False, "error": f"Post {post_id} not found"}
