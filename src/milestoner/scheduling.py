"""Optimal posting time suggestions and scheduling utilities."""

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

# Optimal posting times based on research (US Eastern Time)
# Format: (hour, minute, description)
OPTIMAL_TIMES = {
    0: [(13, 0, "Monday afternoon - 4-5x higher engagement")],  # Monday
    1: [(10, 0, "Tuesday mid-morning"), (12, 0, "Tuesday lunchtime")],  # Tuesday
    2: [
        (10, 0, "Wednesday 10 AM - peak engagement time"),
        (12, 0, "Wednesday noon"),
        (18, 0, "Wednesday evening"),
    ],  # Wednesday
    3: [(10, 0, "Thursday morning"), (17, 0, "Thursday evening")],  # Thursday
    4: [(10, 0, "Friday morning"), (17, 0, "Friday evening")],  # Friday
    5: [(11, 0, "Saturday late morning"), (15, 0, "Saturday afternoon")],  # Saturday
    6: [(11, 0, "Sunday late morning"), (15, 0, "Sunday afternoon")],  # Sunday
}

# Times to avoid
AVOID_TIMES = [
    (23, 6, "Late night to early morning - lowest engagement"),
    (13, 16, "Weekday afternoons - deep work block"),
]


def get_user_timezone() -> ZoneInfo:
    """Get user's timezone. Defaults to US/Eastern."""
    # Could be enhanced to read from config
    return ZoneInfo("US/Eastern")


def get_optimal_times(timezone: ZoneInfo | None = None) -> dict[str, Any]:
    """
    Get optimal posting times for today and upcoming days.

    Returns recommendations based on research showing best engagement times.
    """
    tz = timezone or get_user_timezone()
    now = datetime.now(tz)
    today = now.weekday()

    recommendations = []

    # Check today's remaining optimal times
    today_times = OPTIMAL_TIMES.get(today, [])
    for hour, minute, desc in today_times:
        optimal_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if optimal_time > now:
            recommendations.append(
                {
                    "datetime": optimal_time.isoformat(),
                    "relative": "today",
                    "time": optimal_time.strftime("%I:%M %p"),
                    "day": optimal_time.strftime("%A"),
                    "reason": desc,
                    "priority": "high" if "peak" in desc.lower() else "medium",
                }
            )

    # Add tomorrow's times
    tomorrow = (today + 1) % 7
    tomorrow_date = now + timedelta(days=1)
    tomorrow_times = OPTIMAL_TIMES.get(tomorrow, [])
    for hour, minute, desc in tomorrow_times:
        optimal_time = tomorrow_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        recommendations.append(
            {
                "datetime": optimal_time.isoformat(),
                "relative": "tomorrow",
                "time": optimal_time.strftime("%I:%M %p"),
                "day": optimal_time.strftime("%A"),
                "reason": desc,
                "priority": "high" if "peak" in desc.lower() else "medium",
            }
        )

    # Find next Wednesday 10 AM if not already included (best time overall)
    days_until_wednesday = (2 - today) % 7
    if days_until_wednesday == 0 and now.hour >= 10:
        days_until_wednesday = 7
    next_wednesday = now + timedelta(days=days_until_wednesday)
    next_wednesday_10am = next_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)

    # Current time assessment
    current_quality = _assess_current_time(now)

    return {
        "current_time": now.isoformat(),
        "timezone": str(tz),
        "current_time_quality": current_quality,
        "recommendations": recommendations[:5],  # Top 5 upcoming times
        "best_time_this_week": {
            "datetime": next_wednesday_10am.isoformat(),
            "description": "Wednesday 10 AM - statistically the best time for engagement",
        },
        "times_to_avoid": [
            {"hours": f"{start}:00 - {end}:00", "reason": reason}
            for start, end, reason in AVOID_TIMES
        ],
    }


def _assess_current_time(now: datetime) -> dict[str, Any]:
    """Assess if now is a good time to post."""
    hour = now.hour
    weekday = now.weekday()

    # Check if it's a bad time
    for start, end, reason in AVOID_TIMES:
        if start <= hour < end:
            return {
                "quality": "poor",
                "score": 2,
                "reason": reason,
                "suggestion": "Consider waiting for a better time",
            }

    # Check if it's an optimal time
    today_times = OPTIMAL_TIMES.get(weekday, [])
    for opt_hour, _, desc in today_times:
        if abs(hour - opt_hour) <= 1:  # Within 1 hour of optimal
            return {
                "quality": "excellent" if hour == opt_hour else "good",
                "score": 9 if hour == opt_hour else 7,
                "reason": desc,
                "suggestion": "Great time to post!",
            }

    # Default - okay time
    return {
        "quality": "okay",
        "score": 5,
        "reason": "Not peak engagement time, but acceptable",
        "suggestion": "Posting now is fine, but optimal times may get more engagement",
    }


def suggest_posting_time(content_type: str = "general") -> dict[str, Any]:
    """
    Suggest the best time to post based on content type.

    Args:
        content_type: Type of content - "announcement", "technical", "casual", "engagement"

    Returns:
        Suggestion with reasoning
    """
    tz = get_user_timezone()

    content_suggestions = {
        "announcement": {
            "preferred_times": ["morning", "wednesday"],
            "reason": "Announcements perform best mid-week mornings when attention is highest",
        },
        "technical": {
            "preferred_times": ["morning"],
            "reason": "Technical content does well in morning hours when devs are fresh",
        },
        "casual": {
            "preferred_times": ["lunch", "evening"],
            "reason": "Casual content performs well during breaks and wind-down time",
        },
        "engagement": {
            "preferred_times": ["evening", "weekend"],
            "reason": "Questions and discussions get more replies in evenings/weekends",
        },
    }

    suggestion = content_suggestions.get(content_type, content_suggestions["casual"])
    optimal = get_optimal_times(tz)

    return {
        "content_type": content_type,
        "suggestion": suggestion,
        "optimal_times": optimal,
    }
