from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, UploadFile

from app.domain.schemas import PipelineRunResponse
from app.services.pipeline_service import DocumentPipelineService
from app.storage.audit_repository import AuditRepository

router = APIRouter(prefix="/api/v1", tags=["document-pipeline"])


@router.post("/pipeline/run", response_model=PipelineRunResponse)
async def run_pipeline(file: UploadFile = File(...), source_system: str = "manual_upload") -> PipelineRunResponse:
    suffix = Path(file.filename or "upload.csv").suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    summary = DocumentPipelineService().run(tmp_path, source_system=source_system)
    return PipelineRunResponse(
        run_id=summary.run_id,
        status="completed",
        total_records=summary.total_records,
        auto_process_count=summary.auto_process_count,
        manual_review_count=summary.manual_review_count,
        reject_count=summary.reject_count,
        quality_score=summary.quality_score,
        artifacts=summary.output_files,
    )


@router.get("/pipeline/runs")
def list_runs(limit: int = 20) -> list[dict]:
    return AuditRepository().list_runs(limit=limit)
