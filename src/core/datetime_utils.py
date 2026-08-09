from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current UTC time as a naive datetime.

    The database currently stores naive UTC timestamps.
    This helper avoids deprecated datetime.utcnow() while
    preserving the existing database representation.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
