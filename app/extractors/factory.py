from pathlib import Path

from app.extractors.base import DocumentExtractor
from app.extractors.csv_extractor import CsvExtractor
from app.extractors.pdf_extractor import PdfInvoiceExtractor


class ExtractorRegistry:
    def __init__(self) -> None:
        self._extractors: list[DocumentExtractor] = [CsvExtractor(), PdfInvoiceExtractor()]

    def get(self, file_path: Path) -> DocumentExtractor:
        for extractor in self._extractors:
            if extractor.supports(file_path):
                return extractor
        raise ValueError(f"Unsupported file type: {file_path.suffix}")
