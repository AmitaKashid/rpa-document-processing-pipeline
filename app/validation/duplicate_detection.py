from collections import defaultdict
from itertools import combinations

from rapidfuzz import fuzz

from app.domain.models import BusinessRecord, Severity, ValidationFinding


class DuplicateDetector:
    """Hybrid deterministic + fuzzy duplicate detector for automation safety."""

    def __init__(self, fuzzy_threshold: int = 93) -> None:
        self.fuzzy_threshold = fuzzy_threshold

    def evaluate(self, records: list[BusinessRecord]) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        findings.extend(self._exact_key_duplicates(records))
        findings.extend(self._fuzzy_name_amount_duplicates(records))
        return findings

    def _exact_key_duplicates(self, records: list[BusinessRecord]) -> list[ValidationFinding]:
        buckets: dict[tuple[str | None, str | None], list[BusinessRecord]] = defaultdict(list)
        for record in records:
            if record.invoice_id or record.order_id:
                buckets[(record.invoice_id, record.order_id)].append(record)

        findings: list[ValidationFinding] = []
        for key, grouped in buckets.items():
            if len(grouped) > 1:
                for record in grouped:
                    findings.append(
                        ValidationFinding(
                            record_id=record.record_id,
                            field="invoice_id/order_id",
                            rule_id="DUP_001_EXACT_BUSINESS_KEY",
                            severity=Severity.critical,
                            message=f"Duplicate business key detected: {key}",
                            value=key,
                        )
                    )
        return findings

    def _fuzzy_name_amount_duplicates(self, records: list[BusinessRecord]) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        candidates = [r for r in records if r.customer_name and r.amount is not None]
        for left, right in combinations(candidates, 2):
            if left.record_id == right.record_id or left.amount != right.amount:
                continue
            score = fuzz.token_sort_ratio(left.customer_name or "", right.customer_name or "")
            if score >= self.fuzzy_threshold:
                for record in (left, right):
                    findings.append(
                        ValidationFinding(
                            record_id=record.record_id,
                            field="customer_name/amount",
                            rule_id="DUP_002_FUZZY_NAME_AMOUNT",
                            severity=Severity.warning,
                            message=f"Possible fuzzy duplicate detected with similarity={score}",
                            value={"customer_name": record.customer_name, "amount": record.amount},
                        )
                    )
        return findings
