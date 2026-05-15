from pathlib import Path
import json

import pandas as pd

from app.domain.models import BusinessRecord, PipelineRunSummary, RecordDecision, RoutingDecision


class RpaOutputWriter:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write(self, run_id: str, records: list[BusinessRecord], decisions: list[RecordDecision]) -> dict[str, str]:
        decision_map = {d.record_id: d for d in decisions}
        rows = []
        findings_rows = []

        for record in records:
            decision = decision_map[record.record_id]
            rows.append(
                {
                    "run_id": run_id,
                    "record_id": record.record_id,
                    "document_id": record.document_id,
                    "customer_id": record.customer_id,
                    "invoice_id": record.invoice_id,
                    "order_id": record.order_id,
                    "amount": record.amount,
                    "currency": record.currency,
                    "decision": decision.decision.value,
                    "automation_confidence": decision.automation_confidence,
                    "recommended_queue": decision.recommended_queue,
                }
            )
            for finding in decision.findings:
                findings_rows.append(finding.model_dump())

        ready_path = self.output_dir / f"{run_id}_rpa_ready.csv"
        exception_path = self.output_dir / f"{run_id}_exceptions.csv"
        audit_path = self.output_dir / f"{run_id}_audit.jsonl"

        pd.DataFrame(rows).to_csv(ready_path, index=False)
        pd.DataFrame(findings_rows).to_csv(exception_path, index=False)

        with audit_path.open("w", encoding="utf-8") as file:
            for record in records:
                event = {
                    "record": record.model_dump(mode="json"),
                    "decision": decision_map[record.record_id].model_dump(mode="json"),
                }
                file.write(json.dumps(event, default=str) + "\n")

        auto_ready = self.output_dir / f"{run_id}_automation_only.csv"
        pd.DataFrame([r for r in rows if r["decision"] == RoutingDecision.auto_process.value]).to_csv(
            auto_ready, index=False
        )

        return {
            "rpa_ready_table": str(ready_path),
            "exception_table": str(exception_path),
            "audit_log": str(audit_path),
            "automation_only_table": str(auto_ready),
        }

    def write_summary(self, summary: PipelineRunSummary) -> str:
        summary_path = self.output_dir / f"{summary.run_id}_summary.json"
        summary_path.write_text(summary.model_dump_json(indent=2), encoding="utf-8")
        return str(summary_path)
