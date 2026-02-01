# Calendar Event Exporter

A Python CLI application that fetches events from Google Calendar (via iCal URL or API), filters by hashtags and date ranges, and exports to multiple formats.

## Features

- **Multiple data sources**: Public iCal URLs (.ics feeds) or Google Calendar API
- **Hashtag filtering**: Filter events by hashtags in their descriptions (e.g., `#billable`, `#project`)
- **Flexible date ranges**: Single dates, date ranges, or datetime ranges
- **Multiple export formats**: Terminal, CSV, JSON, XLSX, ODS, PDF

## Installation

### Using pip (recommended)

```bash
pip install -e .
```

### Development installation

```bash
pip install -e ".[dev]"
```

## Usage

### Basic Commands

```bash
# Show help
cal-exporter --help

# Export today's events with a specific hashtag to terminal
cal-exporter -c "https://calendar.google.com/calendar/ical/xxx/public/basic.ics" -s "#billable"

# Export a date range to Excel
cal-exporter -c "primary" -d "2026-02-01:2026-02-28" -s "#project" -w report.xlsx -e xlsx

# Export to PDF
cal-exporter -c "https://calendar.google.com/.../basic.ics" -d "2026-02-01" -s "#work" -w report.pdf -e pdf
```

### CLI Options

| Option | Description |
|--------|-------------|
| `-c, --calendar` | Calendar source - iCal URL or Google Calendar ID (required if not using `-l`) |
| `-l, --local` | Path to a local `.ics` file (required if not using `-c`) |
| `-g, --credentials` | Path to Google API OAuth `credentials.json` file |
| `-s, --search` | Hashtags to filter by (can specify multiple times) |
| `-d, --date` | Date filter: `today`, `YYYY-MM-DD`, or `YYYY-MM-DD:YYYY-MM-DD` |
| `-w, --write` | Output file path |
| `-e, --export` | Export format: `pdf`, `xlsx`, `ods`, `csv`, `json` |
| `-t, --terminal` | Output to terminal (default if no `-w` specified) |

### Date Format Examples

```bash
# Today only (default)
-d "today"

# Single date
-d "2026-02-01"

# Date range
-d "2026-02-01:2026-02-28"

# With time
-d "2026-02-01T09:00:2026-02-01T17:00"
```

### Hashtag Filtering (AND/OR Logic)

The `-s` option supports both AND and OR logic:

- **Comma-separated hashtags** = AND logic (all must be present)
- **Multiple -s options** = OR logic (any group must match)

```bash
# AND logic: Events must have BOTH #zzp AND #hosintra
cal-exporter -c "..." -s "#zzp, #hosintra"

# OR logic: Events must have #billable OR #project OR #meeting
cal-exporter -c "..." -s "#billable" -s "#project" -s "#meeting"

# Combined: Events must have (#zzp AND #work) OR #meeting
cal-exporter -c "..." -s "#zzp, #work" -s "#meeting"
```

## Calendar Sources

### Public iCal URL

For public Google Calendar feeds, use the iCal URL:

1. Open Google Calendar settings
2. Select your calendar
3. Scroll to "Integrate calendar"
4. Copy the "Public address in iCal format"

Example URL:
```
https://calendar.google.com/calendar/ical/your-calendar-id/public/basic.ics
```

### Google Calendar API

For private calendars or more features, use the Google Calendar API:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials (Desktop application type)
5. Download the credentials and save as `credentials.json` in your working directory

Then use the calendar ID with the `-g` option to specify your credentials file:
```bash
# Use "primary" for your main calendar with credentials
cal-exporter -c "primary" -g ~/credentials.json -s "#billable"

# Or use a specific calendar ID
cal-exporter -c "your-calendar-id@group.calendar.google.com" -g ./credentials.json -s "#work"
```

On first run, a browser window will open for authentication. The token is saved to `token.json` for future use.

## Export Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| Terminal | - | Rich formatted table in terminal |
| CSV | `.csv` | Comma-separated values |
| JSON | `.json` | Structured JSON with events and summary |
| XLSX | `.xlsx` | Microsoft Excel format with formatting |
| ODS | `.ods` | OpenDocument Spreadsheet |
| PDF | `.pdf` | Formatted PDF report |

## Example Workflows

### Load from Local File

```bash
# Load events from a local .ics file
cal-exporter -l ~/calendars/work.ics -s "#billable"

# Export local file to CSV
cal-exporter -l exported_calendar.ics -d "2026-02-01:2026-02-28" -w events.csv -e csv
```

### Track Billable Hours

```bash
# Export this week's billable hours to Excel
cal-exporter -c "primary" -d "2026-02-01:2026-02-07" -s "#billable" -w weekly_hours.xlsx -e xlsx
```

### Generate Monthly Report

```bash
# PDF report for the month
cal-exporter -c "..." -d "2026-02-01:2026-02-28" -s "#project" -w february_report.pdf -e pdf
```

### Quick Terminal Check

```bash
# See today's meetings
cal-exporter -c "..." -s "#meeting" -t
```

## Requirements

- Python 3.9+
- Dependencies are managed via `pyproject.toml`

## Troubleshooting

### Library Import Errors

If you encounter import errors with cryptography or PIL/Pillow, the CLI will still work for basic operations. Some export formats may be unavailable if their required libraries have system-level issues.

### Google Calendar API

The Google Calendar API requires proper OAuth setup. If you only need to access public calendars, use the iCal URL method instead, which requires no authentication.

## License

MIT License
