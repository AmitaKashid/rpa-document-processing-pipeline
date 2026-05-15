from pydantic import BaseModel, Field


class PipelineRunRequest(BaseModel):
    source_system: str = "manual_upload"
    document_type_hint: str | None = None
    enable_fuzzy_duplicate_detection: bool = True
    strict_mode: bool = False


class PipelineRunResponse(BaseModel):
    run_id: str
    status: str
    total_records: int
    auto_process_count: int
    manual_review_count: int
    reject_count: int
    quality_score: float = Field(ge=0, le=1)
    artifacts: dict[str, str]
