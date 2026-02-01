"""JSON file exporter."""

import json
from pathlib import Path
from typing import List

from cal_exporter.models import CalendarEvent


class JSONExporter:
    """Export events to JSON file format."""
    
    def __init__(self, output_path: str):
        """
        Initialize the JSON exporter.
        
        Args:
            output_path: Path to the output JSON file
        """
        self.output_path = Path(output_path)
    
    def export(self, events: List[CalendarEvent]) -> None:
        """
        Export events to a JSON file.
        
        Args:
            events: List of calendar events to export
        """
        # Ensure parent directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert events to dictionaries
        data = {
            "events": [event.to_dict() for event in events],
            "summary": {
                "total_events": len(events),
                "total_hours": round(sum(e.duration_hours for e in events), 2),
            }
        }
        
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
