from app.core.config import settings
from app.domain.models import RecordDecision, RoutingDecision, Severity, ValidationFinding


class ExceptionRouter:
    """Maps validation outcomes to RPA-compatible processing queues."""

    def route(self, record_id: str, findings: list[ValidationFinding]) -> RecordDecision:
        critical_count = sum(1 for f in findings if f.severity == Severity.critical)
        warning_count = sum(1 for f in findings if f.severity == Severity.warning)

        confidence = max(0.0, round(1.0 - critical_count * 0.45 - warning_count * 0.15, 4))

        if critical_count >= 2:
            decision = RoutingDecision.reject
            queue = "RPA_REJECTED_DATA_FIX_REQUIRED"
        elif critical_count == 1 or confidence < settings.min_confidence_for_automation:
            decision = RoutingDecision.manual_review
            queue = "RPA_MANUAL_REVIEW_EXCEPTION_QUEUE"
        else:
            decision = RoutingDecision.auto_process
            queue = "RPA_AUTO_PROCESS_READY"

        return RecordDecision(
            record_id=record_id,
            decision=decision,
            automation_confidence=confidence,
            findings=findings,
            recommended_queue=queue,
        )
