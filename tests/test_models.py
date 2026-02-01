"""Tests for the data models."""

import pytest
from datetime import datetime
from dateutil.tz import tzlocal

from cal_exporter.models import CalendarEvent


class TestCalendarEvent:
    """Tests for the CalendarEvent model."""
    
    @pytest.fixture
    def sample_event(self):
        """Create a sample event for testing."""
        local_tz = tzlocal()
        return CalendarEvent(
            summary="Test Meeting",
            start=datetime(2026, 2, 1, 9, 0, tzinfo=local_tz),
            end=datetime(2026, 2, 1, 10, 30, tzinfo=local_tz),
            description="A test meeting #billable #client",
            location="Conference Room",
            uid="test123@calendar",
            hashtags=["#billable", "#client"],
        )
    
    def test_duration_hours(self, sample_event):
        """Duration should be calculated correctly in hours."""
        assert sample_event.duration_hours == 1.5
    
    def test_duration_formatted(self, sample_event):
        """Duration should be formatted as HH:MM."""
        assert sample_event.duration_formatted == "1:30"
    
    def test_duration_formatted_whole_hours(self):
        """Duration formatting for whole hours."""
        local_tz = tzlocal()
        event = CalendarEvent(
            summary="Test",
            start=datetime(2026, 2, 1, 9, 0, tzinfo=local_tz),
            end=datetime(2026, 2, 1, 12, 0, tzinfo=local_tz),
        )
        assert event.duration_formatted == "3:00"
    
    def test_to_dict(self, sample_event):
        """Event should convert to dictionary correctly."""
        result = sample_event.to_dict()
        
        assert result["summary"] == "Test Meeting"
        assert result["duration_hours"] == 1.5
        assert result["duration_formatted"] == "1:30"
        assert result["location"] == "Conference Room"
        assert "#billable" in result["hashtags"]
    
    def test_to_dict_empty_optional_fields(self):
        """Dictionary should handle None optional fields."""
        local_tz = tzlocal()
        event = CalendarEvent(
            summary="Test",
            start=datetime(2026, 2, 1, 9, 0, tzinfo=local_tz),
            end=datetime(2026, 2, 1, 10, 0, tzinfo=local_tz),
        )
        result = event.to_dict()
        
        assert result["description"] == ""
        assert result["location"] == ""
    
    def test_default_hashtags_empty_list(self):
        """Default hashtags should be an empty list."""
        local_tz = tzlocal()
        event = CalendarEvent(
            summary="Test",
            start=datetime(2026, 2, 1, 9, 0, tzinfo=local_tz),
            end=datetime(2026, 2, 1, 10, 0, tzinfo=local_tz),
        )
        assert event.hashtags == []
