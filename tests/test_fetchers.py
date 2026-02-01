"""Tests for the fetcher modules."""

import pytest
from datetime import datetime
from pathlib import Path
from dateutil.tz import tzlocal

from cal_exporter.fetchers import LocalICalFetcher


class TestLocalICalFetcher:
    """Tests for local .ics file fetcher."""
    
    @pytest.fixture
    def test_ics_path(self):
        """Path to the test .ics file."""
        return Path(__file__).parent / "test_calendar.ics"
    
    @pytest.fixture
    def fetcher(self, test_ics_path):
        """Create a fetcher with the test file."""
        return LocalICalFetcher(str(test_ics_path))
    
    def test_fetcher_loads_file(self, fetcher):
        """Fetcher should successfully load the test file."""
        local_tz = tzlocal()
        start = datetime(2026, 2, 1, 0, 0, tzinfo=local_tz)
        end = datetime(2026, 2, 28, 23, 59, tzinfo=local_tz)
        
        events = fetcher.fetch(start, end)
        assert len(events) == 8
    
    def test_fetcher_filters_by_date(self, fetcher):
        """Fetcher should only return events in date range."""
        local_tz = tzlocal()
        start = datetime(2026, 2, 1, 0, 0, tzinfo=local_tz)
        end = datetime(2026, 2, 1, 23, 59, tzinfo=local_tz)
        
        events = fetcher.fetch(start, end)
        assert len(events) == 2  # Only Feb 1 events
    
    def test_fetcher_parses_event_summary(self, fetcher):
        """Fetcher should correctly parse event summaries."""
        local_tz = tzlocal()
        start = datetime(2026, 2, 1, 0, 0, tzinfo=local_tz)
        end = datetime(2026, 2, 1, 23, 59, tzinfo=local_tz)
        
        events = fetcher.fetch(start, end)
        summaries = [e.summary for e in events]
        assert "Client Meeting - Project Alpha" in summaries
    
    def test_fetcher_extracts_hashtags(self, fetcher):
        """Fetcher should extract hashtags from descriptions."""
        local_tz = tzlocal()
        start = datetime(2026, 2, 1, 0, 0, tzinfo=local_tz)
        end = datetime(2026, 2, 1, 23, 59, tzinfo=local_tz)
        
        events = fetcher.fetch(start, end)
        # First event should have #billable, #meeting, #client
        first_event = events[0]
        assert "#billable" in first_event.hashtags
        assert "#meeting" in first_event.hashtags
        assert "#client" in first_event.hashtags
    
    def test_fetcher_calculates_duration(self, fetcher):
        """Fetcher should correctly calculate event duration."""
        local_tz = tzlocal()
        start = datetime(2026, 2, 1, 0, 0, tzinfo=local_tz)
        end = datetime(2026, 2, 1, 23, 59, tzinfo=local_tz)
        
        events = fetcher.fetch(start, end)
        # First event: 09:00-12:00 = 3 hours
        assert events[0].duration_hours == 3.0
    
    def test_fetcher_file_not_found(self):
        """Fetcher should raise error for non-existent file."""
        with pytest.raises(FileNotFoundError):
            LocalICalFetcher("/nonexistent/file.ics")
    
    def test_fetcher_invalid_extension(self, tmp_path):
        """Fetcher should raise error for non-.ics files."""
        bad_file = tmp_path / "calendar.txt"
        bad_file.write_text("not a calendar")
        
        with pytest.raises(ValueError, match=".ics extension"):
            LocalICalFetcher(str(bad_file))
    
    def test_fetcher_events_sorted_by_start(self, fetcher):
        """Events should be sorted by start time."""
        local_tz = tzlocal()
        start = datetime(2026, 2, 1, 0, 0, tzinfo=local_tz)
        end = datetime(2026, 2, 5, 23, 59, tzinfo=local_tz)
        
        events = fetcher.fetch(start, end)
        for i in range(len(events) - 1):
            assert events[i].start <= events[i + 1].start
