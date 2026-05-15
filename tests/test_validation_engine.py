from app.domain.models import BusinessRecord, Severity
from app.validation.engine import ValidationEngine


def test_required_and_amount_rules_are_reported():
    record = BusinessRecord(document_id="doc-1", amount=-10, currency="EUR")
    findings = ValidationEngine().validate([record])[record.record_id]
    rule_ids = {finding.rule_id for finding in findings}

    assert "REQ_001_REQUIRED_CORE_FIELDS" in rule_ids
    assert "AMT_001_POSITIVE_AMOUNT" in rule_ids
    assert any(f.severity == Severity.critical for f in findings)
