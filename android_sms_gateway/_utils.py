import datetime
import typing as t


def _parse_iso(value: t.Optional[str]) -> t.Optional[datetime.datetime]:
    """Parse an ISO 8601 timestamp string to a datetime object.

    Args:
        value: An ISO 8601 timestamp string (e.g., "2024-01-01T12:00:00Z") or None.

    Returns:
        A datetime object or None if value is None.
    """
    if value is None:
        return None
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
