from pathlib import Path
from typing import Any

import pandas as pd

from app.domain.models import BusinessRecord, IngestedDocument
from app.extractors.base import DocumentExtractor


COLUMN_ALIASES = {
    "client_id": "customer_id",
    "cust_id": "customer_id",
    "name": "customer_name",
    "total": "amount",
    "invoice_total": "amount",
    "ccy": "currency",
    "mail": "email",
}


class CsvExtractor(DocumentExtractor):
    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in {".csv", ".tsv"}

    def extract(self, file_path: Path, document: IngestedDocument) -> list[BusinessRecord]:
        sep = "\t" if file_path.suffix.lower() == ".tsv" else ","
        frame = pd.read_csv(file_path, sep=sep).rename(columns=self._normalize_columns)
        records: list[BusinessRecord] = []
        for idx, row in frame.iterrows():
            payload = self._clean_payload(row.to_dict())
            records.append(
                BusinessRecord(
                    document_id=document.document_id,
                    row_number=int(idx) + 1,
                    raw_payload=payload,
                    **{k: v for k, v in payload.items() if k in BusinessRecord.model_fields},
                )
            )
        return records

    @staticmethod
    def _normalize_columns(column: str) -> str:
        normalized = column.strip().lower().replace(" ", "_").replace("-", "_")
        return COLUMN_ALIASES.get(normalized, normalized)

    @staticmethod
    def _clean_payload(payload: dict[str, Any]) -> dict[str, Any]:
        cleaned = {}
        for key, value in payload.items():
            if pd.isna(value):
                cleaned[key] = None
            elif isinstance(value, str):
                cleaned[key] = value.strip()
            else:
                cleaned[key] = value
        return cleaned
