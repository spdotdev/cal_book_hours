"""Export modules for various output formats."""

# Lazy imports to avoid breaking the CLI if some libraries have issues


def get_terminal_exporter():
    """Get TerminalExporter class."""
    from .terminal import TerminalExporter
    return TerminalExporter


def get_csv_exporter():
    """Get CSVExporter class."""
    from .csv_export import CSVExporter
    return CSVExporter


def get_json_exporter():
    """Get JSONExporter class."""
    from .json_export import JSONExporter
    return JSONExporter


def get_xlsx_exporter():
    """Get XLSXExporter class."""
    from .xlsx_export import XLSXExporter
    return XLSXExporter


def get_ods_exporter():
    """Get ODSExporter class."""
    from .ods_export import ODSExporter
    return ODSExporter


def get_pdf_exporter():
    """Get PDFExporter class."""
    from .pdf_export import PDFExporter
    return PDFExporter


__all__ = [
    "get_terminal_exporter",
    "get_csv_exporter",
    "get_json_exporter",
    "get_xlsx_exporter",
    "get_ods_exporter",
    "get_pdf_exporter",
]
