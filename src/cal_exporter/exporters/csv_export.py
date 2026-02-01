"""CSV file exporter."""

import csv
from pathlib import Path
from typing import List

from cal_exporter.models import CalendarEvent


class CSVExporter:
    """Export events to CSV file format."""
    
    def __init__(self, output_path: str):
        """
        Initialize the CSV exporter.
        
        Args:
            output_path: Path to the output CSV file
        """
        self.output_path = Path(output_path)
    
    def export(self, events: List[CalendarEvent]) -> None:
        """
        Export events to a CSV file.
        
        Args:
            events: List of calendar events to export
        """
        if not events:
            return
        
        # Ensure parent directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define columns
        fieldnames = [
            "date",
            "start_time",
            "end_time",
            "duration_hours",
            "duration_formatted",
            "summary",
            "description",
            "location",
            "hashtags",
        ]
        
        with open(self.output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for event in events:
                writer.writerow({
                    "date": event.start.strftime("%Y-%m-%d"),
                    "start_time": event.start.strftime("%H:%M"),
                    "end_time": event.end.strftime("%H:%M"),
                    "duration_hours": round(event.duration_hours, 2),
                    "duration_formatted": event.duration_formatted,
                    "summary": event.summary,
                    "description": event.description or "",
                    "location": event.location or "",
                    "hashtags": ", ".join(event.hashtags),
                })
