"""Local iCal file fetcher."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from icalendar import Calendar
from dateutil.tz import tzlocal

from cal_exporter.models import CalendarEvent
from cal_exporter.filters import extract_hashtags


class LocalICalFetcher:
    """Fetch and parse events from a local .ics file."""
    
    def __init__(self, file_path: str):
        """
        Initialize the local iCal fetcher.
        
        Args:
            file_path: Path to the local .ics file
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"iCal file not found: {file_path}")
        if not self.file_path.suffix.lower() == ".ics":
            raise ValueError(f"File must have .ics extension: {file_path}")
    
    def fetch(self, start: datetime, end: datetime) -> List[CalendarEvent]:
        """
        Fetch events from the local iCal file within the date range.
        
        Args:
            start: Start of date range
            end: End of date range
            
        Returns:
            List of CalendarEvent objects
        """
        # Read the iCal file
        with open(self.file_path, "rb") as f:
            cal = Calendar.from_ical(f.read())
        
        events = []
        local_tz = tzlocal()
        
        for component in cal.walk():
            if component.name != "VEVENT":
                continue
            
            event = self._parse_event(component, local_tz)
            if event is None:
                continue
            
            # Filter by date range
            if event.start <= end and event.end >= start:
                events.append(event)
        
        # Sort by start time
        events.sort(key=lambda e: e.start)
        
        return events
    
    def _parse_event(self, component, local_tz) -> Optional[CalendarEvent]:
        """Parse a VEVENT component into a CalendarEvent."""
        try:
            # Get summary
            summary = str(component.get("summary", "No Title"))
            
            # Get start/end times
            dtstart = component.get("dtstart")
            dtend = component.get("dtend")
            
            if dtstart is None:
                return None
            
            start_dt = self._normalize_datetime(dtstart.dt, local_tz)
            
            if dtend is not None:
                end_dt = self._normalize_datetime(dtend.dt, local_tz)
            else:
                # If no end time, assume 1 hour duration
                end_dt = start_dt.replace(hour=start_dt.hour + 1)
            
            # Get description
            description = component.get("description")
            if description:
                description = str(description)
            
            # Get location
            location = component.get("location")
            if location:
                location = str(location)
            
            # Get UID
            uid = component.get("uid")
            if uid:
                uid = str(uid)
            
            # Extract hashtags from description
            hashtags = extract_hashtags(description)
            
            return CalendarEvent(
                summary=summary,
                start=start_dt,
                end=end_dt,
                description=description,
                location=location,
                uid=uid,
                hashtags=hashtags,
            )
            
        except Exception:
            # Skip malformed events
            return None
    
    def _normalize_datetime(self, dt, local_tz) -> datetime:
        """
        Normalize a datetime value to a timezone-aware datetime.
        
        Handles both date and datetime objects from icalendar.
        """
        from datetime import date, time
        
        # If it's a date (not datetime), convert to datetime at midnight
        if not isinstance(dt, datetime):
            if isinstance(dt, date):
                dt = datetime.combine(dt, time.min)
        
        # Add timezone if missing
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=local_tz)
        else:
            # Convert to local timezone for consistency
            dt = dt.astimezone(local_tz)
        
        return dt
