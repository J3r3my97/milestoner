from typing import Any

from ..git.history import format_commits_for_display, get_activity_summary, get_commits
from ..platforms.registry import get_platform, list_platforms


def draft_update(
    context: str | None = None,
    style: str = "casual",
    repo_path: str | None = None,
    commit_range: str | None = None,
    platform: str | None = None,
) -> dict[str, Any]:
    """
    Generate structured context for drafting a social media post.

    This returns context for the host LLM (Claude) to generate the actual post.
    We don't generate the post ourselves - we provide the data.

    Args:
        context: Additional context or what to focus on (e.g., "just shipped auth")
        style: Tone of post - "casual", "announcement", "technical", "storytelling"
        repo_path: Path to git repo (defaults to current directory)
        commit_range: Specific commits (e.g., "abc123..def456" or "last 5")
        platform: Target platform (defaults to configured default)

    Returns:
        Structured context for post generation
    """
    # Determine platform
    if platform is None:
        from ..config.store import get_default_platform

        platform = get_default_platform()

    # Validate platform
    if platform not in list_platforms():
        return {
            "error": f"Unknown platform: {platform}. Available: {', '.join(list_platforms())}",
        }

    # Get platform info
    platform_instance = get_platform(platform)
    char_limit = platform_instance.character_limit

    # Get git context
    try:
        if commit_range:
            commits = get_commits(repo_path=repo_path, commit_range=commit_range)
        else:
            # Default to recent commits
            commits = get_commits(repo_path=repo_path, since="7 days")
    except ValueError as e:
        return {"error": str(e)}

    formatted_commits = format_commits_for_display(commits)
    summary = get_activity_summary(commits)

    # Style guidance for the LLM
    style_guidance = {
        "casual": "Friendly, conversational tone. Like talking to a friend about what you built.",
        "announcement": "Professional but excited. Announcing a milestone or release.",
        "technical": "Focus on the technical details. What was implemented, how it works.",
        "storytelling": "Tell the journey. The problem, the struggle, the solution.",
    }

    return {
        "platform": platform,
        "character_limit": char_limit,
        "user_context": context,
        "style": style,
        "style_guidance": style_guidance.get(style, style_guidance["casual"]),
        "git_context": {
            "commits": formatted_commits[:10],  # Limit to 10 most recent
            "summary": summary,
        },
        "instructions": (
            f"Generate a {platform} post ({char_limit} char max) based on this git activity. "
            f"Style: {style}. "
            f"User wants to highlight: {context or 'general progress'}. "
            "Keep it authentic and avoid corporate speak. "
            "Optionally suggest 1-2 relevant hashtags at the end."
        ),
    }
