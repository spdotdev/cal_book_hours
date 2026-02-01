"""Tests for the filtering module."""

import pytest
from datetime import datetime
from dateutil.tz import tzlocal

from cal_exporter.filters import (
    parse_date_range,
    extract_hashtags,
    filter_events,
    _parse_hashtag_groups,
    _normalize_hashtag,
)
from cal_exporter.models import CalendarEvent


class TestExtractHashtags:
    """Tests for hashtag extraction."""
    
    def test_extract_single_hashtag(self):
        text = "This is a #test description"
        result = extract_hashtags(text)
        assert result == ["#test"]
    
    def test_extract_multiple_hashtags(self):
        text = "Meeting about #project and #client #billable"
        result = extract_hashtags(text)
        assert result == ["#project", "#client", "#billable"]
    
    def test_extract_no_hashtags(self):
        text = "This has no hashtags"
        result = extract_hashtags(text)
        assert result == []
    
    def test_extract_from_none(self):
        result = extract_hashtags(None)
        assert result == []
    
    def test_extract_from_empty_string(self):
        result = extract_hashtags("")
        assert result == []


class TestNormalizeHashtag:
    """Tests for hashtag normalization."""
    
    def test_normalize_with_hash(self):
        assert _normalize_hashtag("#Test") == "#test"
    
    def test_normalize_without_hash(self):
        assert _normalize_hashtag("test") == "#test"
    
    def test_normalize_with_whitespace(self):
        assert _normalize_hashtag("  #test  ") == "#test"


class TestParseHashtagGroups:
    """Tests for AND/OR hashtag group parsing."""
    
    def test_single_hashtag(self):
        result = _parse_hashtag_groups(["#billable"])
        assert result == [{"#billable"}]
    
    def test_multiple_or_groups(self):
        result = _parse_hashtag_groups(["#billable", "#meeting"])
        assert result == [{"#billable"}, {"#meeting"}]
    
    def test_comma_separated_and_group(self):
        result = _parse_hashtag_groups(["#zzp, #hosintra"])
        assert result == [{"#zzp", "#hosintra"}]
    
    def test_combined_and_or(self):
        result = _parse_hashtag_groups(["#zzp, #work", "#meeting"])
        assert result == [{"#zzp", "#work"}, {"#meeting"}]


class TestParseDateRange:
    """Tests for date range parsing."""
    
    def test_parse_today(self):
        start, end = parse_date_range("today")
        assert start.hour == 0
        assert start.minute == 0
        assert end.hour == 23
        assert end.minute == 59
    
    def test_parse_single_date(self):
        start, end = parse_date_range("2026-02-15")
        assert start.year == 2026
        assert start.month == 2
        assert start.day == 15
        assert start.hour == 0
        assert end.hour == 23
    
    def test_parse_date_range(self):
        start, end = parse_date_range("2026-02-01:2026-02-28")
        assert start.day == 1
        assert end.day == 28
    
    def test_invalid_date_raises_error(self):
        with pytest.raises(ValueError):
            parse_date_range("not-a-date")


class TestFilterEvents:
    """Tests for event filtering with AND/OR logic."""
    
    @pytest.fixture
    def sample_events(self):
        """Create sample events for testing."""
        local_tz = tzlocal()
        return [
            CalendarEvent(
                summary="Event 1",
                start=datetime(2026, 2, 1, 9, 0, tzinfo=local_tz),
                end=datetime(2026, 2, 1, 10, 0, tzinfo=local_tz),
                description="Task with #billable #client",
            ),
            CalendarEvent(
                summary="Event 2",
                start=datetime(2026, 2, 1, 11, 0, tzinfo=local_tz),
                end=datetime(2026, 2, 1, 12, 0, tzinfo=local_tz),
                description="Task with #zzp #hosintra #billable",
            ),
            CalendarEvent(
                summary="Event 3",
                start=datetime(2026, 2, 1, 14, 0, tzinfo=local_tz),
                end=datetime(2026, 2, 1, 15, 0, tzinfo=local_tz),
                description="Task with #meeting",
            ),
            CalendarEvent(
                summary="Event 4",
                start=datetime(2026, 2, 1, 16, 0, tzinfo=local_tz),
                end=datetime(2026, 2, 1, 17, 0, tzinfo=local_tz),
                description="No hashtags here",
            ),
        ]
    
    def test_filter_no_hashtags_returns_all(self, sample_events):
        """When no hashtags specified, return all events."""
        result = filter_events(sample_events, [])
        assert len(result) == 4
    
    def test_filter_single_hashtag_or(self, sample_events):
        """Single hashtag should match events with that hashtag."""
        result = filter_events(sample_events, ["#billable"])
        assert len(result) == 2
        assert result[0].summary == "Event 1"
        assert result[1].summary == "Event 2"
    
    def test_filter_multiple_hashtags_or(self, sample_events):
        """Multiple -s options = OR logic."""
        result = filter_events(sample_events, ["#meeting", "#client"])
        assert len(result) == 2  # Event 1 (client) and Event 3 (meeting)
    
    def test_filter_comma_separated_and(self, sample_events):
        """Comma-separated hashtags = AND logic."""
        result = filter_events(sample_events, ["#zzp, #hosintra"])
        assert len(result) == 1
        assert result[0].summary == "Event 2"
    
    def test_filter_and_no_match(self, sample_events):
        """AND logic with no matching event."""
        result = filter_events(sample_events, ["#billable, #meeting"])
        assert len(result) == 0
    
    def test_filter_combined_and_or(self, sample_events):
        """Combined AND/OR: (#zzp AND #hosintra) OR #meeting."""
        result = filter_events(sample_events, ["#zzp, #hosintra", "#meeting"])
        assert len(result) == 2
        summaries = [e.summary for e in result]
        assert "Event 2" in summaries  # has #zzp AND #hosintra
        assert "Event 3" in summaries  # has #meeting
    
    def test_filter_case_insensitive(self, sample_events):
        """Hashtag matching should be case-insensitive."""
        result = filter_events(sample_events, ["#BILLABLE"])
        assert len(result) == 2
    
    def test_filter_without_hash_prefix(self, sample_events):
        """Hashtags without # prefix should still work."""
        result = filter_events(sample_events, ["billable"])
        assert len(result) == 2
