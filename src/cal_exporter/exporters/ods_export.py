"""OpenDocument Spreadsheet (ODS) file exporter using pyexcel-ods3."""

from pathlib import Path
from typing import List

from pyexcel_ods3 import save_data

from cal_exporter.models import CalendarEvent


class ODSExporter:
    """Export events to OpenDocument Spreadsheet (ODS) file format."""
    
    def __init__(self, output_path: str):
        """
        Initialize the ODS exporter.
        
        Args:
            output_path: Path to the output ODS file
        """
        self.output_path = Path(output_path)
    
    def export(self, events: List[CalendarEvent]) -> None:
        """
        Export events to an ODS file.
        
        Args:
            events: List of calendar events to export
        """
        # Ensure parent directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define headers
        headers = [
            "Date",
            "Start Time",
            "End Time",
            "Duration (h)",
            "Duration",
            "Summary",
            "Description",
            "Location",
            "Hashtags",
        ]
        
        # Build data rows
        rows = [headers]
        
        for event in events:
            row = [
                event.start.strftime("%Y-%m-%d"),
                event.start.strftime("%H:%M"),
                event.end.strftime("%H:%M"),
                round(event.duration_hours, 2),
                event.duration_formatted,
                event.summary,
                event.description or "",
                event.location or "",
                ", ".join(event.hashtags),
            ]
            rows.append(row)
        
        # Add empty row and summary
        rows.append([])
        rows.append(["Total Events:", len(events)])
        rows.append(["Total Hours:", round(sum(e.duration_hours for e in events), 2)])
        
        # Save to ODS file
        data = {"Calendar Events": rows}
        save_data(str(self.output_path), data)
