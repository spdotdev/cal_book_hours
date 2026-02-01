"""Command-line interface for the calendar exporter."""

import sys
from pathlib import Path
from typing import Optional, Tuple

import click

from cal_exporter.fetchers import ICalFetcher, LocalICalFetcher, get_google_api_fetcher
from cal_exporter.filters import filter_events, parse_date_range
from cal_exporter.exporters import (
    get_terminal_exporter,
    get_csv_exporter,
    get_json_exporter,
    get_xlsx_exporter,
    get_ods_exporter,
    get_pdf_exporter,
)


def get_fetcher(calendar: str, credentials: Optional[str] = None):
    """Determine the appropriate fetcher based on the calendar source."""
    # Check if it's an iCal URL
    if calendar.startswith(("http://", "https://")) and (
        ".ics" in calendar or "ical" in calendar.lower()
    ):
        return ICalFetcher(calendar)
    
    # Otherwise, treat as Google Calendar ID
    try:
        GoogleAPIFetcher = get_google_api_fetcher()
        return GoogleAPIFetcher(calendar, credentials_file=credentials)
    except ImportError as e:
        raise ImportError(
            "Google Calendar API libraries are not available. "
            "Please use an iCal URL instead, or install the Google API dependencies: "
            "pip install google-api-python-client google-auth-oauthlib"
        ) from e


def get_exporter(export_format: str, output_path: Optional[str]):
    """Get the appropriate exporter based on format."""
    exporter_getters = {
        "csv": get_csv_exporter,
        "json": get_json_exporter,
        "xlsx": get_xlsx_exporter,
        "ods": get_ods_exporter,
        "pdf": get_pdf_exporter,
    }
    
    if export_format in exporter_getters:
        try:
            ExporterClass = exporter_getters[export_format]()
            return ExporterClass(output_path)
        except ImportError as e:
            raise ImportError(f"Export format '{export_format}' is not available: {e}")
    
    return None


@click.command()
@click.option(
    "-c", "--calendar",
    help="Google Calendar public iCal URL or Calendar ID for API access."
)
@click.option(
    "-l", "--local",
    type=click.Path(exists=True),
    help="Path to a local .ics file to load."
)
@click.option(
    "-s", "--search",
    multiple=True,
    help="Hashtags to filter by. Comma-separated = AND logic, multiple -s = OR logic. "
         "Example: -s '#zzp, #work' requires both; -s '#zzp' -s '#work' requires either."
)
@click.option(
    "-d", "--date",
    default="today",
    help="Date filter: single date (YYYY-MM-DD), range (YYYY-MM-DD:YYYY-MM-DD), "
         "or 'today'. Supports time: YYYY-MM-DDTHH:MM"
)
@click.option(
    "-w", "--write",
    type=click.Path(),
    help="Output file path to write results to."
)
@click.option(
    "-e", "--export",
    type=click.Choice(["pdf", "xlsx", "ods", "csv", "json"], case_sensitive=False),
    help="Export format (required when using -w)."
)
@click.option(
    "-t", "--terminal",
    is_flag=True,
    default=False,
    help="Output results to terminal (default if no -w specified)."
)
@click.option(
    "-g", "--credentials",
    type=click.Path(exists=True),
    help="Path to Google API OAuth credentials.json file (for Google Calendar API access)."
)
@click.version_option(package_name="cal-exporter")
def main(calendar: Optional[str], local: Optional[str], search: Tuple[str, ...], 
         date: str, write: Optional[str], export: Optional[str], terminal: bool,
         credentials: Optional[str]):
    """
    Export Google Calendar events filtered by hashtags.
    
    Examples:
    
    \b
    # Export today's events with #billable tag to terminal
    cal-exporter -c "https://calendar.google.com/.../basic.ics" -s "#billable"
    
    \b
    # Load a local .ics file
    cal-exporter -l calendar.ics -s "#billable"
    
    \b
    # Export date range to Excel
    cal-exporter -c "primary" -d "2026-02-01:2026-02-28" -s "#project" -w report.xlsx -e xlsx
    
    \b
    # Use Google Calendar API with credentials file
    cal-exporter -c "primary" -g ~/credentials.json -s "#work"
    """
    # Validate that either -c or -l is provided
    if not calendar and not local:
        raise click.UsageError("You must specify either -c/--calendar or -l/--local")
    
    if calendar and local:
        raise click.UsageError("Cannot use both -c/--calendar and -l/--local. Choose one.")
    
    # Validate arguments
    if write and not export:
        # Try to infer format from file extension
        path = Path(write)
        ext = path.suffix.lower().lstrip(".")
        if ext in ["pdf", "xlsx", "ods", "csv", "json"]:
            export = ext
        else:
            raise click.UsageError(
                "When using -w/--write, you must specify -e/--export format "
                "or use a recognized file extension (.pdf, .xlsx, .ods, .csv, .json)"
            )
    
    # Default to terminal output if no write path specified
    if not write:
        terminal = True
    
    try:
        # Parse date range
        start_date, end_date = parse_date_range(date)
        click.echo(f"Filtering events from {start_date} to {end_date}", err=True)
        
        # Get the appropriate fetcher
        if local:
            fetcher = LocalICalFetcher(local)
            click.echo(f"Loading events from local file: {local}", err=True)
        else:
            fetcher = get_fetcher(calendar, credentials)
            click.echo(f"Fetching events from calendar...", err=True)
        
        # Fetch events
        events = fetcher.fetch(start_date, end_date)
        click.echo(f"Found {len(events)} events in date range.", err=True)
        
        # Filter by hashtags if specified
        if search:
            events = filter_events(events, list(search))
            click.echo(f"After hashtag filter: {len(events)} events.", err=True)
        
        if not events:
            click.echo("No events found matching your criteria.", err=True)
            sys.exit(0)
        
        # Export to file if specified
        if write and export:
            exporter = get_exporter(export.lower(), write)
            if exporter:
                exporter.export(events)
                click.echo(f"Exported to {write}", err=True)
        
        # Output to terminal
        if terminal:
            TerminalExporter = get_terminal_exporter()
            terminal_exporter = TerminalExporter()
            terminal_exporter.export(events)
            
    except Exception as e:
        raise click.ClickException(str(e))


if __name__ == "__main__":
    main()
