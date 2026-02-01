"""Event filtering by date range and hashtags."""

import re
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from dateutil import parser as date_parser
from dateutil.tz import tzlocal

from cal_exporter.models import CalendarEvent


def parse_date_range(date_string: str) -> Tuple[datetime, datetime]:
    """
    Parse a date string into start and end datetime objects.
    
    Supported formats:
    - "today" - current day from 00:00 to 23:59
    - "YYYY-MM-DD" - single date from 00:00 to 23:59
    - "YYYY-MM-DD:YYYY-MM-DD" - date range
    - "YYYY-MM-DDTHH:MM:YYYY-MM-DDTHH:MM" - datetime range
    
    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    date_string = date_string.strip()
    local_tz = tzlocal()
    
    if date_string.lower() == "today":
        today = datetime.now(local_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        return today, today.replace(hour=23, minute=59, second=59)
    
    # Check for range separator
    if ":" in date_string:
        # Could be a time separator or a range separator
        # Try to split on the range pattern
        parts = _split_date_range(date_string)
        if len(parts) == 2:
            start = _parse_single_date(parts[0], is_start=True)
            end = _parse_single_date(parts[1], is_start=False)
            return start, end
    
    # Single date
    start = _parse_single_date(date_string, is_start=True)
    end = start.replace(hour=23, minute=59, second=59)
    return start, end


def _split_date_range(date_string: str) -> List[str]:
    """
    Split a date range string handling both date and time separators.
    
    Examples:
    - "2026-02-01:2026-02-28" -> ["2026-02-01", "2026-02-28"]
    - "2026-02-01T09:00:2026-02-01T17:00" -> ["2026-02-01T09:00", "2026-02-01T17:00"]
    """
    # Pattern to match date or datetime followed by : and another date/datetime
    # Look for the pattern where we have a date, then :, then another date
    pattern = r'^(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2})?):(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2})?)$'
    match = re.match(pattern, date_string)
    
    if match:
        return [match.group(1), match.group(2)]
    
    # Fallback: just return the original string as a single item
    return [date_string]


def _parse_single_date(date_string: str, is_start: bool = True) -> datetime:
    """
    Parse a single date/datetime string.
    
    Args:
        date_string: The date string to parse
        is_start: If True, defaults time to 00:00:00, otherwise 23:59:59
    """
    local_tz = tzlocal()
    
    try:
        dt = date_parser.parse(date_string)
        
        # If no timezone, assume local
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=local_tz)
        
        # If only date was provided (no time component in string), set appropriate time
        if "T" not in date_string and " " not in date_string:
            if is_start:
                dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                dt = dt.replace(hour=23, minute=59, second=59, microsecond=0)
        
        return dt
        
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid date format: {date_string}. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM") from e


def extract_hashtags(text: Optional[str]) -> List[str]:
    """
    Extract hashtags from text.
    
    Args:
        text: Text to search for hashtags
        
    Returns:
        List of hashtags found (including the # symbol)
    """
    if not text:
        return []
    
    # Match hashtags: # followed by word characters
    pattern = r'#\w+'
    return re.findall(pattern, text, re.IGNORECASE)


def _normalize_hashtag(tag: str) -> str:
    """Normalize a single hashtag (ensure it starts with #, lowercase)."""
    tag = tag.strip()
    if not tag.startswith("#"):
        tag = f"#{tag}"
    return tag.lower()


def _parse_hashtag_groups(hashtags: List[str]) -> List[set]:
    """
    Parse hashtag search terms into groups for AND/OR logic.
    
    - Comma-separated hashtags within a single -s option = AND (all must match)
    - Multiple -s options = OR (any group must match)
    
    Args:
        hashtags: List of search terms from -s options
        
    Returns:
        List of sets, where each set is an AND group
    """
    groups = []
    for search_term in hashtags:
        # Split by comma for AND logic within a single -s option
        if "," in search_term:
            tags_in_group = [_normalize_hashtag(t) for t in search_term.split(",")]
            groups.append(set(tags_in_group))
        else:
            groups.append({_normalize_hashtag(search_term)})
    return groups


def filter_events(
    events: List[CalendarEvent],
    hashtags: List[str],
) -> List[CalendarEvent]:
    """
    Filter events by hashtags in their description.
    
    Supports AND/OR logic:
    - Comma-separated hashtags in a single -s: AND logic (all must be present)
    - Multiple -s options: OR logic (any group must match)
    
    Examples:
    - -s "#zzp, #work" → Event must have BOTH #zzp AND #work
    - -s "#zzp" -s "#work" → Event must have #zzp OR #work
    - -s "#zzp, #work" -s "#meeting" → Event must have (#zzp AND #work) OR #meeting
    
    Args:
        events: List of calendar events
        hashtags: List of hashtag search terms (can contain comma-separated values)
        
    Returns:
        Filtered list of events matching the hashtag criteria
    """
    if not hashtags:
        return events
    
    # Parse hashtags into AND groups (OR between groups)
    hashtag_groups = _parse_hashtag_groups(hashtags)
    
    filtered = []
    for event in events:
        # Extract hashtags from description
        event_hashtags = extract_hashtags(event.description)
        event_hashtags_lower = {t.lower() for t in event_hashtags}
        
        # Check if any AND group is fully satisfied (OR between groups)
        matches = False
        for and_group in hashtag_groups:
            # All hashtags in the group must be present (AND logic)
            if and_group.issubset(event_hashtags_lower):
                matches = True
                break
        
        if matches:
            # Update the event with its hashtags
            event.hashtags = event_hashtags
            filtered.append(event)
    
    return filtered


def filter_by_date_range(
    events: List[CalendarEvent],
    start: datetime,
    end: datetime,
) -> List[CalendarEvent]:
    """
    Filter events that fall within the specified date range.
    
    An event is included if it overlaps with the date range.
    """
    filtered = []
    for event in events:
        # Event overlaps with range if event starts before range ends
        # and event ends after range starts
        if event.start <= end and event.end >= start:
            filtered.append(event)
    
    return filtered
