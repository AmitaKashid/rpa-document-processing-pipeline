from datetime import datetime, timezone
import json

from sqlalchemy import DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.core.config import settings
from app.domain.models import PipelineRunSummary


class Base(DeclarativeBase):
    pass


class PipelineRunORM(Base):
    __tablename__ = "pipeline_runs"

    run_id: Mapped[str] = mapped_column(String, primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    total_records: Mapped[int] = mapped_column(Integer)
    auto_process_count: Mapped[int] = mapped_column(Integer)
    manual_review_count: Mapped[int] = mapped_column(Integer)
    reject_count: Mapped[int] = mapped_column(Integer)
    quality_score: Mapped[float] = mapped_column(Float)
    output_files_json: Mapped[str] = mapped_column(Text)


engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    Base.metadata.create_all(engine)


class AuditRepository:
    def save_run(self, summary: PipelineRunSummary) -> None:
        with SessionLocal() as session:
            session.merge(
                PipelineRunORM(
                    run_id=summary.run_id,
                    started_at=summary.started_at.replace(tzinfo=None),
                    total_records=summary.total_records,
                    auto_process_count=summary.auto_process_count,
                    manual_review_count=summary.manual_review_count,
                    reject_count=summary.reject_count,
                    quality_score=summary.quality_score,
                    output_files_json=json.dumps(summary.output_files),
                )
            )
            session.commit()

    def list_runs(self, limit: int = 20) -> list[dict]:
        with SessionLocal() as session:
            rows = session.query(PipelineRunORM).order_by(PipelineRunORM.started_at.desc()).limit(limit).all()
            return [
                {
                    "run_id": row.run_id,
                    "started_at": row.started_at.isoformat(),
                    "total_records": row.total_records,
                    "quality_score": row.quality_score,
                    "output_files": json.loads(row.output_files_json),
                }
                for row in rows
            ]
