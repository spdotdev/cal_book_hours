"""PDF file exporter using reportlab."""

from pathlib import Path
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from cal_exporter.models import CalendarEvent


class PDFExporter:
    """Export events to PDF file format."""
    
    def __init__(self, output_path: str):
        """
        Initialize the PDF exporter.
        
        Args:
            output_path: Path to the output PDF file
        """
        self.output_path = Path(output_path)
    
    def export(self, events: List[CalendarEvent]) -> None:
        """
        Export events to a PDF file.
        
        Args:
            events: List of calendar events to export
        """
        # Ensure parent directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create document
        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=landscape(letter),
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = styles["Heading1"]
        
        # Create content elements
        elements = []
        
        # Add title
        elements.append(Paragraph("Calendar Events Report", title_style))
        elements.append(Spacer(1, 0.25 * inch))
        
        # Define headers
        headers = [
            "Date",
            "Start",
            "End",
            "Hours",
            "Summary",
            "Hashtags",
        ]
        
        # Build table data
        table_data = [headers]
        
        for event in events:
            row = [
                event.start.strftime("%Y-%m-%d"),
                event.start.strftime("%H:%M"),
                event.end.strftime("%H:%M"),
                f"{event.duration_hours:.2f}",
                self._truncate(event.summary, 50),
                self._truncate(", ".join(event.hashtags), 30),
            ]
            table_data.append(row)
        
        # Create table
        col_widths = [1 * inch, 0.7 * inch, 0.7 * inch, 0.7 * inch, 4 * inch, 2 * inch]
        table = Table(table_data, colWidths=col_widths)
        
        # Style the table
        table.setStyle(TableStyle([
            # Header style
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            
            # Body style
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (0, 1), (3, -1), "CENTER"),  # Center date/time columns
            ("ALIGN", (3, 1), (3, -1), "RIGHT"),  # Right align hours
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
            
            # Alternating row colors
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
            
            # Grid
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.25 * inch))
        
        # Add summary
        total_hours = sum(e.duration_hours for e in events)
        summary_style = ParagraphStyle(
            "Summary",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
        )
        elements.append(Paragraph(f"Total Events: {len(events)}", summary_style))
        elements.append(Paragraph(f"Total Hours: {total_hours:.2f}", summary_style))
        
        # Build PDF
        doc.build(elements)
    
    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to max length with ellipsis."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
