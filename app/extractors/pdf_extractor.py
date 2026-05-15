from pathlib import Path
import re

import pdfplumber

from app.domain.models import BusinessRecord, IngestedDocument
from app.extractors.base import DocumentExtractor


class PdfInvoiceExtractor(DocumentExtractor):
    """Deterministic PDF extractor for invoice-like semi-structured documents.

    Recruiter signal: instead of pretending every PDF is solved by OCR/LLMs, this extractor
    separates deterministic field extraction from validation and exception handling.
    """

    FIELD_PATTERNS = {
        "invoice_id": re.compile(r"Invoice\s*(?:No|ID|Number)[:#]?\s*([A-Z0-9-]+)", re.I),
        "customer_id": re.compile(r"Customer\s*(?:No|ID)[:#]?\s*([A-Z0-9-]+)", re.I),
        "amount": re.compile(r"(?:Total|Amount Due)[:\s]+(?:EUR|USD|GBP)?\s*([0-9,.]+)", re.I),
        "currency": re.compile(r"\b(EUR|USD|GBP|CHF)\b", re.I),
        "invoice_date": re.compile(r"Invoice Date[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}\.[0-9]{2}\.[0-9]{4})", re.I),
        "due_date": re.compile(r"Due Date[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}\.[0-9]{2}\.[0-9]{4})", re.I),
        "iban": re.compile(r"\b([A-Z]{2}[0-9]{2}[A-Z0-9]{10,30})\b"),
        "email": re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I),
    }

    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".pdf"

    def extract(self, file_path: Path, document: IngestedDocument) -> list[BusinessRecord]:
        text = self._read_text(file_path)
        payload = {field: self._match(pattern, text) for field, pattern in self.FIELD_PATTERNS.items()}
        if payload.get("amount"):
            payload["amount"] = float(str(payload["amount"]).replace(".", "").replace(",", "."))
        payload["raw_text_excerpt"] = text[:1500]
        return [BusinessRecord(document_id=document.document_id, row_number=1, raw_payload=payload, **payload)]

    @staticmethod
    def _read_text(file_path: Path) -> str:
        pages: list[str] = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
        return "\n".join(pages)

    @staticmethod
    def _match(pattern: re.Pattern[str], text: str) -> str | None:
        found = pattern.search(text)
        return found.group(1).strip() if found and found.groups() else found.group(0).strip() if found else None
