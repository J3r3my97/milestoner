from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from git import Repo
from git.exc import InvalidGitRepositoryError


@dataclass
class CommitInfo:
    """Information about a single commit."""

    hash: str
    short_hash: str
    message: str
    author: str
    date: datetime
    files_changed: list[str]
    insertions: int
    deletions: int


def get_repo(repo_path: str | None = None) -> Repo:
    """Get a git repo object from a path."""
    path = Path(repo_path) if repo_path else Path.cwd()
    try:
        return Repo(path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise ValueError(f"Not a git repository: {path}")


def parse_since(since: str) -> datetime:
    """Parse a 'since' string like '7 days' or '2 weeks' into a datetime."""
    since = since.lower().strip()
    now = datetime.now()

    # Parse common formats
    parts = since.split()
    if len(parts) == 2:
        try:
            amount = int(parts[0])
            unit = parts[1].rstrip("s")  # Remove trailing 's' for plurals

            if unit == "day":
                return now - timedelta(days=amount)
            elif unit == "week":
                return now - timedelta(weeks=amount)
            elif unit == "month":
                return now - timedelta(days=amount * 30)
            elif unit == "hour":
                return now - timedelta(hours=amount)
        except ValueError:
            pass

    # Default to 7 days if parsing fails
    return now - timedelta(days=7)


def get_commits(
    repo_path: str | None = None,
    since: str = "7 days",
    commit_range: str | None = None,
) -> list[CommitInfo]:
    """
    Get commits from a git repository.

    Args:
        repo_path: Path to the git repo (defaults to current directory)
        since: How far back to look (e.g., "7 days", "2 weeks")
        commit_range: Specific commit range (e.g., "abc123..def456" or "last 5")

    Returns:
        List of CommitInfo objects, newest first
    """
    repo = get_repo(repo_path)
    commits: list[CommitInfo] = []

    if commit_range:
        # Handle "last N" format
        if commit_range.lower().startswith("last "):
            try:
                n = int(commit_range.split()[1])
                commit_iter = list(repo.iter_commits(max_count=n))
            except (ValueError, IndexError):
                commit_iter = list(repo.iter_commits(max_count=10))
        # Handle "abc..def" format
        elif ".." in commit_range:
            commit_iter = list(repo.iter_commits(commit_range))
        else:
            # Single commit hash
            commit_iter = [repo.commit(commit_range)]
    else:
        # Get commits since date
        since_date = parse_since(since)
        commit_iter = list(repo.iter_commits(since=since_date))

    for commit in commit_iter:
        # Get stats for this commit
        stats = commit.stats
        files = list(stats.files.keys())

        commits.append(
            CommitInfo(
                hash=commit.hexsha,
                short_hash=commit.hexsha[:7],
                message=commit.message.strip(),
                author=commit.author.name or "Unknown",
                date=datetime.fromtimestamp(commit.committed_date),
                files_changed=files,
                insertions=stats.total["insertions"],
                deletions=stats.total["deletions"],
            )
        )

    return commits


def group_commits_by_day(commits: list[CommitInfo]) -> dict[str, list[CommitInfo]]:
    """Group commits by date."""
    groups: dict[str, list[CommitInfo]] = {}
    for commit in commits:
        date_key = commit.date.strftime("%Y-%m-%d")
        if date_key not in groups:
            groups[date_key] = []
        groups[date_key].append(commit)
    return groups


def format_commits_for_display(commits: list[CommitInfo]) -> list[dict[str, Any]]:
    """Format commits for tool output."""
    return [
        {
            "hash": c.short_hash,
            "message": c.message.split("\n")[0],  # First line only
            "author": c.author,
            "date": c.date.isoformat(),
            "files_changed": c.files_changed,
            "stats": f"+{c.insertions}/-{c.deletions}",
        }
        for c in commits
    ]


def get_activity_summary(commits: list[CommitInfo]) -> dict[str, Any]:
    """Generate a summary of commit activity."""
    if not commits:
        return {
            "total_commits": 0,
            "files_changed": [],
            "total_insertions": 0,
            "total_deletions": 0,
            "date_range": None,
        }

    all_files: set[str] = set()
    total_insertions = 0
    total_deletions = 0

    for commit in commits:
        all_files.update(commit.files_changed)
        total_insertions += commit.insertions
        total_deletions += commit.deletions

    return {
        "total_commits": len(commits),
        "files_changed": sorted(all_files),
        "total_insertions": total_insertions,
        "total_deletions": total_deletions,
        "date_range": {
            "oldest": commits[-1].date.isoformat() if commits else None,
            "newest": commits[0].date.isoformat() if commits else None,
        },
    }
