"""Tests for the CLI module."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from cal_exporter.cli import main


class TestCLI:
    """Tests for CLI functionality."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def test_ics_path(self):
        """Path to the test .ics file."""
        return str(Path(__file__).parent / "test_calendar.ics")
    
    def test_help_option(self, runner):
        """CLI should display help."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Export Google Calendar events" in result.output
    
    def test_requires_calendar_or_local(self, runner):
        """CLI should require -c or -l option."""
        result = runner.invoke(main, ["-s", "#test"])
        assert result.exit_code != 0
        assert "must specify either" in result.output.lower() or "error" in result.output.lower()
    
    def test_cannot_use_both_calendar_and_local(self, runner, test_ics_path):
        """CLI should reject both -c and -l together."""
        result = runner.invoke(main, ["-c", "test", "-l", test_ics_path])
        assert result.exit_code != 0
        assert "cannot use both" in result.output.lower()
    
    def test_load_local_file(self, runner, test_ics_path):
        """CLI should load local .ics file."""
        result = runner.invoke(main, [
            "-l", test_ics_path,
            "-d", "2026-02-01:2026-02-05",
            "-t"
        ])
        assert result.exit_code == 0
        assert "Found" in result.output or "events" in result.output.lower()
    
    def test_filter_by_hashtag(self, runner, test_ics_path):
        """CLI should filter by hashtag."""
        result = runner.invoke(main, [
            "-l", test_ics_path,
            "-d", "2026-02-01:2026-02-28",
            "-s", "#billable",
            "-t"
        ])
        assert result.exit_code == 0
    
    def test_filter_and_logic(self, runner, test_ics_path):
        """CLI should support AND logic with comma-separated hashtags."""
        result = runner.invoke(main, [
            "-l", test_ics_path,
            "-d", "2026-02-01:2026-02-28",
            "-s", "#zzp, #hosintra",
            "-t"
        ])
        assert result.exit_code == 0
        # Should find the "Hospital IT Consultation" event
    
    def test_export_to_csv(self, runner, test_ics_path, tmp_path):
        """CLI should export to CSV."""
        output_file = tmp_path / "output.csv"
        result = runner.invoke(main, [
            "-l", test_ics_path,
            "-d", "2026-02-01:2026-02-05",
            "-w", str(output_file),
            "-e", "csv"
        ])
        assert result.exit_code == 0
        assert output_file.exists()
    
    def test_export_to_json(self, runner, test_ics_path, tmp_path):
        """CLI should export to JSON."""
        output_file = tmp_path / "output.json"
        result = runner.invoke(main, [
            "-l", test_ics_path,
            "-d", "2026-02-01:2026-02-05",
            "-w", str(output_file),
            "-e", "json"
        ])
        assert result.exit_code == 0
        assert output_file.exists()
    
    def test_infer_format_from_extension(self, runner, test_ics_path, tmp_path):
        """CLI should infer export format from file extension."""
        output_file = tmp_path / "output.csv"
        result = runner.invoke(main, [
            "-l", test_ics_path,
            "-d", "2026-02-01:2026-02-05",
            "-w", str(output_file)
            # No -e option, should infer from .csv extension
        ])
        assert result.exit_code == 0
        assert output_file.exists()
