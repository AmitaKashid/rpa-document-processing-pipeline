from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable
import re

from app.domain.models import BusinessRecord, Severity, ValidationFinding


class ValidationRule(ABC):
    rule_id: str
    severity: Severity

    @abstractmethod
    def evaluate(self, record: BusinessRecord) -> Iterable[ValidationFinding]: ...

    def finding(self, record: BusinessRecord, field: str | None, message: str, value=None) -> ValidationFinding:
        return ValidationFinding(
            record_id=record.record_id,
            field=field,
            rule_id=self.rule_id,
            severity=self.severity,
            message=message,
            value=value,
        )


class RequiredFieldsRule(ValidationRule):
    rule_id = "REQ_001_REQUIRED_CORE_FIELDS"
    severity = Severity.critical

    def __init__(self, fields: list[str]) -> None:
        self.fields = fields

    def evaluate(self, record: BusinessRecord) -> Iterable[ValidationFinding]:
        for field in self.fields:
            value = getattr(record, field, None)
            if value in (None, ""):
                yield self.finding(record, field, "Required field is missing", value)


class PositiveAmountRule(ValidationRule):
    rule_id = "AMT_001_POSITIVE_AMOUNT"
    severity = Severity.critical

    def evaluate(self, record: BusinessRecord) -> Iterable[ValidationFinding]:
        if record.amount is not None and record.amount <= 0:
            yield self.finding(record, "amount", "Amount must be greater than zero", record.amount)


class CurrencyWhitelistRule(ValidationRule):
    rule_id = "CUR_001_SUPPORTED_CURRENCY"
    severity = Severity.warning

    def __init__(self, allowed: set[str] | None = None) -> None:
        self.allowed = allowed or {"EUR", "USD", "GBP", "CHF"}

    def evaluate(self, record: BusinessRecord) -> Iterable[ValidationFinding]:
        if record.currency and record.currency not in self.allowed:
            yield self.finding(record, "currency", "Unsupported currency", record.currency)


class EmailFormatRule(ValidationRule):
    rule_id = "CNT_001_EMAIL_FORMAT"
    severity = Severity.warning
    pattern = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.I)

    def evaluate(self, record: BusinessRecord) -> Iterable[ValidationFinding]:
        if record.email and not self.pattern.match(record.email):
            yield self.finding(record, "email", "Email has invalid format", record.email)


class DueDateAfterInvoiceDateRule(ValidationRule):
    rule_id = "DAT_001_DUE_AFTER_INVOICE"
    severity = Severity.warning

    def evaluate(self, record: BusinessRecord) -> Iterable[ValidationFinding]:
        if not record.invoice_date or not record.due_date:
            return
        invoice_date = self._parse(record.invoice_date)
        due_date = self._parse(record.due_date)
        if invoice_date and due_date and due_date < invoice_date:
            yield self.finding(record, "due_date", "Due date is earlier than invoice date", record.due_date)

    @staticmethod
    def _parse(value: str) -> datetime | None:
        for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None
