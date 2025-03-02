import os
from datetime import datetime, timezone, date, time
from decimal import Decimal
from typing import List, Optional, Union, Any
from uuid import UUID
import pytz
def make_json_serializable(data: Any) -> Any:
    """
    Recursively converts objects that aren't JSON serializable into serializable formats.
    Currently handles:
    - UUID -> str
    - datetime -> ISO format str
    - date -> ISO format str
    - time -> ISO format str
    - Decimal -> float
    - Sets -> Lists

    Args:
        data: Any Python object that might contain non-serializable types

    Returns:
        The same data structure with all objects converted to JSON serializable types
    """
    # Handle None
    if data is None:
        return None

    # Handle UUID objects
    if isinstance(data, UUID):
        return str(data)

    # Handle datetime objects
    if isinstance(data, datetime):
        return data.isoformat()

    # Handle date objects
    if isinstance(data, date):
        return data.isoformat()

    # Handle time objects
    if isinstance(data, time):
        return data.isoformat()

    # Handle Decimal objects
    if isinstance(data, Decimal):
        return float(data)

    # Handle dictionaries
    if isinstance(data, dict):
        return {key: make_json_serializable(value) for key, value in data.items()}

    # Handle sets - convert to list
    if isinstance(data, set):
        return list(make_json_serializable(item) for item in data)

    # Handle lists and tuples
    if isinstance(data, (list, tuple)):
        return list(make_json_serializable(item) for item in data)

    # Return unchanged data for other types
    return data


def convert_to_mountain_time(dt: Optional[Union[datetime, date]]) -> Optional[datetime]:
    """
    Converts a given datetime or date object to Mountain Time (America/Denver).
    If the input has no timezone, UTC is assumed.

    Args:
        dt (Optional[Union[datetime, date]]): The input datetime or date object.

    Returns:
        Optional[datetime]: A datetime object converted to Mountain Time, or None if the input is None.
    """
    if not dt:
        return None

    if isinstance(dt, date) and not isinstance(dt, datetime):
        # Convert date to datetime for timezone conversion
        dt = datetime.combine(dt, datetime.min.time())

    mt_timezone = pytz.timezone("America/Denver")

    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)

    return dt.astimezone(mt_timezone)
def safe_format_date(dt: Optional[Union[date, datetime]], format_str: str) -> str:
    """
    Safely formats a date or datetime object to a string using the provided format.
    If the input is None, an empty string is returned.

    Supports cross-platform date formatting for Windows and Unix-based systems.

    Args:
        dt (Optional[Union[date, datetime]]): The date or datetime object to format.
        format_str (str): The format string for strftime.

    Returns:
        str: The formatted date as a string, or an empty string if the input is None.
    """
    if dt is None:
        return ""

    # Convert to Mountain Time if necessary
    dt = convert_to_mountain_time(dt)

    # Adjust format string for Windows compatibility
    if os.name == "nt":
        format_str = format_str.replace("%-m", "%#m").replace("%-d", "%#d")

    return dt.strftime(format_str)
