"""Google Calendar API fetcher using OAuth2 authentication."""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

from dateutil import parser as date_parser
from dateutil.tz import tzlocal

from cal_exporter.models import CalendarEvent
from cal_exporter.filters import extract_hashtags


# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False


# OAuth2 scopes required for reading calendar events
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Default paths for credentials
DEFAULT_CREDENTIALS_FILE = "credentials.json"
DEFAULT_TOKEN_FILE = "token.json"


class GoogleAPIFetcher:
    """Fetch events from Google Calendar using the API."""
    
    def __init__(
        self,
        calendar_id: str = "primary",
        credentials_file: Optional[str] = None,
        token_file: Optional[str] = None,
    ):
        """
        Initialize the Google Calendar API fetcher.
        
        Args:
            calendar_id: The calendar ID to fetch from (default: "primary")
            credentials_file: Path to OAuth credentials JSON file
            token_file: Path to store/read OAuth token
        """
        if not GOOGLE_API_AVAILABLE:
            raise ImportError(
                "Google API libraries not installed. "
                "Install with: pip install google-api-python-client google-auth-oauthlib"
            )
        
        self.calendar_id = calendar_id
        self.credentials_file = credentials_file or DEFAULT_CREDENTIALS_FILE
        self.token_file = token_file or DEFAULT_TOKEN_FILE
        self._service = None
    
    def _get_credentials(self) -> Credentials:
        """
        Get or refresh OAuth2 credentials.
        
        This will prompt for browser authentication if needed.
        """
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        # Refresh or get new credentials if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"OAuth credentials file not found: {self.credentials_file}\n"
                        "Please download credentials.json from Google Cloud Console:\n"
                        "1. Go to https://console.cloud.google.com/\n"
                        "2. Create a project and enable Google Calendar API\n"
                        "3. Create OAuth 2.0 credentials (Desktop application)\n"
                        "4. Download and save as credentials.json"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
        
        return creds
    
    def _get_service(self):
        """Get or create the Google Calendar API service."""
        if self._service is None:
            creds = self._get_credentials()
            self._service = build("calendar", "v3", credentials=creds)
        return self._service
    
    def fetch(self, start: datetime, end: datetime) -> List[CalendarEvent]:
        """
        Fetch events from Google Calendar within the date range.
        
        Args:
            start: Start of date range
            end: End of date range
            
        Returns:
            List of CalendarEvent objects
        """
        service = self._get_service()
        
        # Format times for API (RFC3339)
        time_min = start.isoformat()
        time_max = end.isoformat()
        
        events = []
        page_token = None
        
        while True:
            # Fetch events from API
            events_result = service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
                pageToken=page_token,
            ).execute()
            
            # Parse events
            for item in events_result.get("items", []):
                event = self._parse_event(item)
                if event:
                    events.append(event)
            
            # Check for more pages
            page_token = events_result.get("nextPageToken")
            if not page_token:
                break
        
        return events
    
    def _parse_event(self, item: dict) -> Optional[CalendarEvent]:
        """Parse a Google Calendar API event item into a CalendarEvent."""
        try:
            summary = item.get("summary", "No Title")
            
            # Get start time
            start_data = item.get("start", {})
            start_str = start_data.get("dateTime") or start_data.get("date")
            if not start_str:
                return None
            
            start_dt = self._parse_datetime(start_str)
            
            # Get end time
            end_data = item.get("end", {})
            end_str = end_data.get("dateTime") or end_data.get("date")
            if end_str:
                end_dt = self._parse_datetime(end_str)
            else:
                # Default to 1 hour duration
                end_dt = start_dt.replace(hour=start_dt.hour + 1)
            
            # Get description
            description = item.get("description")
            
            # Get location
            location = item.get("location")
            
            # Get UID
            uid = item.get("id")
            
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
            return None
    
    def _parse_datetime(self, dt_string: str) -> datetime:
        """Parse a datetime string from the Google Calendar API."""
        local_tz = tzlocal()
        dt = date_parser.parse(dt_string)
        
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=local_tz)
        
        return dt
