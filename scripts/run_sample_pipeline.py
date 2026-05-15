from pathlib import Path
from rich.console import Console
from rich.table import Table

from app.storage.audit_repository import init_db
from app.services.pipeline_service import DocumentPipelineService

console = Console()


def main() -> None:
    init_db()
    summary = DocumentPipelineService().run(Path("data/samples/invoices.csv"), source_system="sample_batch")

    table = Table(title="RPA Document Pipeline Run")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Run ID", summary.run_id)
    table.add_row("Total Records", str(summary.total_records))
    table.add_row("Auto Process", str(summary.auto_process_count))
    table.add_row("Manual Review", str(summary.manual_review_count))
    table.add_row("Rejected", str(summary.reject_count))
    table.add_row("Quality Score", str(summary.quality_score))
    console.print(table)

    console.print("\nArtifacts:")
    for name, path in summary.output_files.items():
        console.print(f"- [bold]{name}[/bold]: {path}")


if __name__ == "__main__":
    main()
