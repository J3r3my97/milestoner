from typing import Any

from ..git.history import (
    format_commits_for_display,
    get_activity_summary,
    get_commits,
    group_commits_by_day,
)


def list_activity(
    repo_path: str | None = None,
    since: str = "7 days",
) -> dict[str, Any]:
    """
    List recent git activity that could be posted about.

    Args:
        repo_path: Path to git repo (defaults to current directory)
        since: How far back to look (e.g., "7 days", "2 weeks")

    Returns:
        Dict containing commits grouped by day and a summary
    """
    try:
        commits = get_commits(repo_path=repo_path, since=since)
    except ValueError as e:
        return {"error": str(e), "commits": [], "summary": {}, "grouped_by_day": {}}

    formatted = format_commits_for_display(commits)
    summary = get_activity_summary(commits)
    grouped = group_commits_by_day(commits)

    # Format grouped commits for display
    grouped_formatted: dict[str, list[dict[str, Any]]] = {}
    for date_key, day_commits in grouped.items():
        grouped_formatted[date_key] = format_commits_for_display(day_commits)

    return {
        "commits": formatted,
        "summary": summary,
        "grouped_by_day": grouped_formatted,
    }
