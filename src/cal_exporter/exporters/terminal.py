"""Terminal output exporter using rich for formatted tables."""

from typing import List

from rich.console import Console
from rich.table import Table

from cal_exporter.models import CalendarEvent


class TerminalExporter:
    """Export events to terminal with formatted table output."""
    
    def __init__(self):
        """Initialize the terminal exporter."""
        self.console = Console()
    
    def export(self, events: List[CalendarEvent]) -> None:
        """
        Export events to the terminal as a formatted table.
        
        Args:
            events: List of calendar events to display
        """
        if not events:
            self.console.print("[yellow]No events to display.[/yellow]")
            return
        
        # Create table
        table = Table(
            title="Calendar Events",
            show_header=True,
            header_style="bold cyan",
        )
        
        # Add columns
        table.add_column("Date", style="green", no_wrap=True)
        table.add_column("Time", style="green", no_wrap=True)
        table.add_column("Duration", style="yellow", justify="right")
        table.add_column("Summary", style="white")
        table.add_column("Hashtags", style="magenta")
        
        # Add rows
        total_hours = 0.0
        for event in events:
            date_str = event.start.strftime("%Y-%m-%d")
            time_str = f"{event.start.strftime('%H:%M')} - {event.end.strftime('%H:%M')}"
            duration = event.duration_formatted
            hashtags = ", ".join(event.hashtags) if event.hashtags else ""
            
            table.add_row(
                date_str,
                time_str,
                duration,
                event.summary,
                hashtags,
            )
            
            total_hours += event.duration_hours
        
        # Print table
        self.console.print(table)
        
        # Print summary
        self.console.print()
        self.console.print(f"[bold]Total events:[/bold] {len(events)}")
        self.console.print(f"[bold]Total hours:[/bold] {total_hours:.2f}")
