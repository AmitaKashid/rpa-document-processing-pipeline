from app.domain.models import Severity, ValidationFinding, RoutingDecision
from app.rpa.routing import ExceptionRouter


def test_router_rejects_records_with_multiple_critical_findings():
    findings = [
        ValidationFinding(record_id="r1", rule_id="A", severity=Severity.critical, message="x"),
        ValidationFinding(record_id="r1", rule_id="B", severity=Severity.critical, message="y"),
    ]

    decision = ExceptionRouter().route("r1", findings)

    assert decision.decision == RoutingDecision.reject
    assert decision.recommended_queue == "RPA_REJECTED_DATA_FIX_REQUIRED"
