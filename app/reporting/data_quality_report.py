from collections import Counter
from pathlib import Path

from jinja2 import Template

from app.domain.models import PipelineRunSummary, RecordDecision


REPORT_TEMPLATE = """
# Data Quality and Automation Readiness Report

## Executive Summary
- Run ID: `{{ summary.run_id }}`
- Total records processed: **{{ summary.total_records }}**
- Automation-ready records: **{{ summary.auto_process_count }}**
- Manual-review records: **{{ summary.manual_review_count }}**
- Rejected records: **{{ summary.reject_count }}**
- Quality score: **{{ summary.quality_score }}**

## Top Automation Blockers
{% for rule_id, count in blockers %}
- `{{ rule_id }}`: {{ count }} affected record(s)
{% endfor %}

## Recruiter-Visible Design Notes
This report demonstrates process-mining thinking: the pipeline does not only validate files; it identifies recurring automation blockers, separates clean-through processing from exception handling, and produces queue-oriented outputs usable by RPA tools.
"""


class DataQualityReportBuilder:
    def write_markdown(self, summary: PipelineRunSummary, decisions: list[RecordDecision], output_dir: Path) -> str:
        counter: Counter[str] = Counter()
        for decision in decisions:
            for finding in decision.findings:
                counter[finding.rule_id] += 1

        report = Template(REPORT_TEMPLATE).render(summary=summary, blockers=counter.most_common(10))
        path = output_dir / f"{summary.run_id}_quality_report.md"
        path.write_text(report.strip() + "\n", encoding="utf-8")
        return str(path)
