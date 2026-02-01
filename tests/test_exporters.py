"""Tests for the exporter modules."""

import json
import csv
import pytest
from datetime import datetime
from pathlib import Path
from dateutil.tz import tzlocal

from cal_exporter.models import CalendarEvent
from cal_exporter.exporters import get_csv_exporter, get_json_exporter


class TestCSVExporter:
    """Tests for CSV export functionality."""
    
    @pytest.fixture
    def sample_events(self):
        """Create sample events for export testing."""
        local_tz = tzlocal()
        return [
            CalendarEvent(
                summary="Meeting 1",
                start=datetime(2026, 2, 1, 9, 0, tzinfo=local_tz),
                end=datetime(2026, 2, 1, 10, 0, tzinfo=local_tz),
                description="Test #billable",
                hashtags=["#billable"],
            ),
            CalendarEvent(
                summary="Meeting 2",
                start=datetime(2026, 2, 1, 14, 0, tzinfo=local_tz),
                end=datetime(2026, 2, 1, 16, 0, tzinfo=local_tz),
                description="Test #work",
                hashtags=["#work"],
            ),
        ]
    
    def test_csv_export_creates_file(self, sample_events, tmp_path):
        """CSV exporter should create the output file."""
        output_file = tmp_path / "output.csv"
        
        CSVExporter = get_csv_exporter()
        exporter = CSVExporter(str(output_file))
        exporter.export(sample_events)
        
        assert output_file.exists()
    
    def test_csv_export_content(self, sample_events, tmp_path):
        """CSV exporter should write correct content."""
        output_file = tmp_path / "output.csv"
        
        CSVExporter = get_csv_exporter()
        exporter = CSVExporter(str(output_file))
        exporter.export(sample_events)
        
        with open(output_file, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 2
        assert rows[0]["summary"] == "Meeting 1"
        assert rows[0]["duration_hours"] == "1.0"
        assert rows[1]["summary"] == "Meeting 2"


class TestJSONExporter:
    """Tests for JSON export functionality."""
    
    @pytest.fixture
    def sample_events(self):
        """Create sample events for export testing."""
        local_tz = tzlocal()
        return [
            CalendarEvent(
                summary="Event 1",
                start=datetime(2026, 2, 1, 9, 0, tzinfo=local_tz),
                end=datetime(2026, 2, 1, 11, 0, tzinfo=local_tz),
                description="Test #billable",
                hashtags=["#billable"],
            ),
        ]
    
    def test_json_export_creates_file(self, sample_events, tmp_path):
        """JSON exporter should create the output file."""
        output_file = tmp_path / "output.json"
        
        JSONExporter = get_json_exporter()
        exporter = JSONExporter(str(output_file))
        exporter.export(sample_events)
        
        assert output_file.exists()
    
    def test_json_export_content(self, sample_events, tmp_path):
        """JSON exporter should write correct structure."""
        output_file = tmp_path / "output.json"
        
        JSONExporter = get_json_exporter()
        exporter = JSONExporter(str(output_file))
        exporter.export(sample_events)
        
        with open(output_file) as f:
            data = json.load(f)
        
        assert "events" in data
        assert "summary" in data
        assert len(data["events"]) == 1
        assert data["events"][0]["summary"] == "Event 1"
        assert data["summary"]["total_events"] == 1
        assert data["summary"]["total_hours"] == 2.0
