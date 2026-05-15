from pathlib import Path

from app.core.config import settings
from app.domain.models import DocumentType, IngestedDocument, PipelineRunSummary, RoutingDecision
from app.extractors.factory import ExtractorRegistry
from app.reporting.data_quality_report import DataQualityReportBuilder
from app.rpa.output_writer import RpaOutputWriter
from app.rpa.routing import ExceptionRouter
from app.storage.audit_repository import AuditRepository
from app.validation.engine import ValidationEngine


class DocumentPipelineService:
    @staticmethod
    def _safe_document_type(value: str | None) -> DocumentType:
        try:
            return DocumentType(value) if value else DocumentType.unknown
        except ValueError:
            return DocumentType.unknown

    def __init__(self) -> None:
        self.extractors = ExtractorRegistry()
        self.validator = ValidationEngine()
        self.router = ExceptionRouter()
        self.writer = RpaOutputWriter(settings.output_dir)
        self.reporter = DataQualityReportBuilder()
        self.audit_repo = AuditRepository()

    def run(self, file_path: Path, source_system: str = "manual_upload", document_type_hint: str | None = None) -> PipelineRunSummary:
        document = IngestedDocument(
            filename=file_path.name,
            source_system=source_system,
            document_type=self._safe_document_type(document_type_hint),
        )
        extractor = self.extractors.get(file_path)
        records = extractor.extract(file_path, document)
        findings_by_record = self.validator.validate(records)

        decisions = [self.router.route(record.record_id, findings_by_record.get(record.record_id, [])) for record in records]
        quality_score = self.validator.quality_score(records, findings_by_record)

        summary = PipelineRunSummary(
            total_records=len(records),
            auto_process_count=sum(1 for d in decisions if d.decision == RoutingDecision.auto_process),
            manual_review_count=sum(1 for d in decisions if d.decision == RoutingDecision.manual_review),
            reject_count=sum(1 for d in decisions if d.decision == RoutingDecision.reject),
            quality_score=quality_score,
        )
        output_files = self.writer.write(summary.run_id, records, decisions)
        output_files["summary"] = self.writer.write_summary(summary)
        output_files["quality_report"] = self.reporter.write_markdown(summary, decisions, settings.output_dir)
        summary.output_files = output_files
        self.audit_repo.save_run(summary)
        return summary
