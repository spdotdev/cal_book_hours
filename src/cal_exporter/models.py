"""Data models for calendar events."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class CalendarEvent:
    """Represents a calendar event with relevant fields for export."""
    
    summary: str
    start: datetime
    end: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    uid: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)
    
    @property
    def duration_hours(self) -> float:
        """Calculate event duration in hours."""
        delta = self.end - self.start
        return delta.total_seconds() / 3600
    
    @property
    def duration_formatted(self) -> str:
        """Format duration as HH:MM."""
        total_minutes = int(self.duration_hours * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours}:{minutes:02d}"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert event to dictionary for export."""
        return {
            "summary": self.summary,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "duration_hours": round(self.duration_hours, 2),
            "duration_formatted": self.duration_formatted,
            "description": self.description or "",
            "location": self.location or "",
            "hashtags": ", ".join(self.hashtags),
        }
