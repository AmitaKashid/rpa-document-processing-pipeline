from collections import defaultdict

from app.domain.models import BusinessRecord, Severity, ValidationFinding
from app.validation.duplicate_detection import DuplicateDetector
from app.validation.rules import (
    CurrencyWhitelistRule,
    DueDateAfterInvoiceDateRule,
    EmailFormatRule,
    PositiveAmountRule,
    RequiredFieldsRule,
    ValidationRule,
)


class ValidationEngine:
    def __init__(self, rules: list[ValidationRule] | None = None) -> None:
        self.rules = rules or [
            RequiredFieldsRule(["customer_id", "amount", "currency"]),
            PositiveAmountRule(),
            CurrencyWhitelistRule(),
            EmailFormatRule(),
            DueDateAfterInvoiceDateRule(),
        ]
        self.duplicate_detector = DuplicateDetector()

    def validate(self, records: list[BusinessRecord]) -> dict[str, list[ValidationFinding]]:
        findings: list[ValidationFinding] = []
        for record in records:
            for rule in self.rules:
                findings.extend(list(rule.evaluate(record)))
        findings.extend(self.duplicate_detector.evaluate(records))

        by_record: dict[str, list[ValidationFinding]] = defaultdict(list)
        for finding in findings:
            by_record[finding.record_id].append(finding)
        return dict(by_record)

    @staticmethod
    def quality_score(records: list[BusinessRecord], findings_by_record: dict[str, list[ValidationFinding]]) -> float:
        if not records:
            return 0.0
        penalty = 0.0
        for findings in findings_by_record.values():
            for finding in findings:
                penalty += 0.25 if finding.severity == Severity.warning else 0.6
        return max(0.0, round(1 - penalty / max(len(records), 1), 4))
