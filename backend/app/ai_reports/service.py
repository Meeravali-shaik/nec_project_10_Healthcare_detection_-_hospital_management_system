from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from html import escape as html_escape
from xml.sax.saxutils import escape as xml_escape
from zipfile import ZIP_DEFLATED, ZipFile

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from sqlalchemy.orm import Session

from app.insights.service import InsightService
from app.models.assistant import GeneratedReport
from app.schemas.assistant import GeneratedReportCreate


class AIReportService:
    def __init__(self, output_dir: str | Path = "generated_reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.insight_service = InsightService()

    def _safe_name(self, value: str) -> str:
        return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value).strip("_").lower()

    def _write_pdf(self, path: Path, title: str, summary: str, narrative: str, metadata: dict) -> None:
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(str(path), pagesize=A4)
        story = [
            Paragraph(html_escape(title), styles["Title"]),
            Spacer(1, 12),
            Paragraph(html_escape(summary), styles["BodyText"]),
            Spacer(1, 12),
            Paragraph(html_escape(narrative), styles["BodyText"]),
            Spacer(1, 12),
            Paragraph(html_escape(f"Metadata: {metadata}"), styles["Code"]),
        ]
        doc.build(story)

    def _write_docx(self, path: Path, title: str, summary: str, narrative: str, metadata: dict) -> None:
        document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>{xml_escape(title)}</w:t></w:r></w:p>
    <w:p><w:r><w:t>{xml_escape(summary)}</w:t></w:r></w:p>
    <w:p><w:r><w:t>{xml_escape(narrative)}</w:t></w:r></w:p>
    <w:p><w:r><w:t>{xml_escape(f"Metadata: {metadata}")}</w:t></w:r></w:p>
  </w:body>
</w:document>"""
        content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="R1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        with ZipFile(path, "w", compression=ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types)
            zf.writestr("_rels/.rels", rels)
            zf.writestr("word/document.xml", document_xml)

    def generate_report(self, db: Session, current_user_id: int | None, payload: GeneratedReportCreate) -> GeneratedReport:
        title = payload.title
        summary = payload.summary
        narrative = payload.metadata_json.get("narrative") or payload.summary
        file_stub = self._safe_name(f"{payload.report_type}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
        format_upper = payload.format.upper()
        if format_upper == "DOCX":
            file_name = f"{file_stub}.docx"
            output_path = self.output_dir / file_name
            self._write_docx(output_path, title, summary, narrative, payload.metadata_json)
        else:
            file_name = f"{file_stub}.pdf"
            output_path = self.output_dir / file_name
            self._write_pdf(output_path, title, summary, narrative, payload.metadata_json)

        report = GeneratedReport(
            report_type=payload.report_type,
            format=format_upper,
            title=title,
            file_name=file_name,
            output_path=str(output_path),
            summary=summary,
            metadata_json=payload.metadata_json,
            created_by=current_user_id,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report
