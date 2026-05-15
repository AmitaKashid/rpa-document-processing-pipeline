from pathlib import Path

from app.services.pipeline_service import DocumentPipelineService
from app.storage.audit_repository import init_db


def test_sample_pipeline_creates_artifacts(tmp_path, monkeypatch):
    init_db()
    summary = DocumentPipelineService().run(Path("data/samples/invoices.csv"), source_system="pytest")

    assert summary.total_records == 6
    assert summary.manual_review_count + summary.reject_count >= 1
    assert "rpa_ready_table" in summary.output_files
