from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DocumentType(str, Enum):
    invoice = "invoice"
    order = "order"
    customer_master = "customer_master"
    unknown = "unknown"


class Severity(str, Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class RoutingDecision(str, Enum):
    auto_process = "AUTO_PROCESS"
    manual_review = "MANUAL_REVIEW"
    reject = "REJECT"


class IngestedDocument(BaseModel):
    document_id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    document_type: DocumentType = DocumentType.unknown
    source_system: str = "manual_upload"
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class BusinessRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    record_id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    row_number: int | None = None
    customer_id: str | None = None
    invoice_id: str | None = None
    order_id: str | None = None
    customer_name: str | None = None
    country: str | None = None
    amount: float | None = None
    currency: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    iban: str | None = None
    email: str | None = None
    raw_payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        return value.upper().strip() if value else value


class ValidationFinding(BaseModel):
    record_id: str
    field: str | None = None
    rule_id: str
    severity: Severity
    message: str
    value: Any = None


class RecordDecision(BaseModel):
    record_id: str
    decision: RoutingDecision
    automation_confidence: float
    findings: list[ValidationFinding] = Field(default_factory=list)
    recommended_queue: str


class PipelineRunSummary(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_records: int
    auto_process_count: int
    manual_review_count: int
    reject_count: int
    quality_score: float
    output_files: dict[str, str] = Field(default_factory=dict)
