# RPA-Ready Document Processing and Data Validation Pipeline

A production-style Python project that ingests business documents, extracts structured records, validates data quality, routes exceptions, and produces RPA-ready handoff tables for tools such as n8n, UiPath-style automations, or internal workflow engines.

This project is intentionally designed as a **recruiter-facing engineering portfolio project**. It is not a single notebook. It demonstrates backend architecture, document extraction, validation design, exception handling, auditability, testability, and automation-readiness.

---

## Business Problem

Organizations often receive invoices, order files, customer master data, reports, or semi-structured documents that must be checked before automation can safely process them. A weak automation pipeline fails when records contain missing fields, duplicate invoices, invalid dates, unsupported currencies, malformed emails, or ambiguous extracted values.

This project solves that problem by separating records into:

1. **Automation-ready records**
2. **Manual-review exceptions**
3. **Rejected records requiring data correction**

The output is designed so an RPA/workflow tool can immediately consume the clean records and route problematic records to the correct exception queue.

---

## Architecture

```text
PDF / CSV / semi-structured business files
        ↓
Document ingestion layer
        ↓
Extractor registry
        ├── CSV / TSV extractor
        └── PDF invoice extractor
        ↓
Canonical business record model
        ↓
Validation engine
        ├── required-field checks
        ├── amount checks
        ├── currency whitelist
        ├── email format checks
        ├── invoice/due-date consistency
        └── exact + fuzzy duplicate detection
        ↓
Exception router
        ├── AUTO_PROCESS
        ├── MANUAL_REVIEW
        └── REJECT
        ↓
RPA-ready outputs
        ├── automation_only.csv
        ├── rpa_ready.csv
        ├── exceptions.csv
        ├── audit.jsonl
        └── data-quality report
        ↓
FastAPI + SQLite audit history
```

---

## Features

### 1. RPA-oriented design, not just ETL

Most beginner projects stop at extraction. This project goes further by producing queue-oriented outputs that are compatible with downstream automation tools.

Example queues:

- `RPA_AUTO_PROCESS_READY`
- `RPA_MANUAL_REVIEW_EXCEPTION_QUEUE`
- `RPA_REJECTED_DATA_FIX_REQUIRED`

### 2. Exception routing with automation confidence

Each record receives an automation confidence score based on validation findings. This mimics real enterprise controls where automation should not blindly process low-quality data.

### 3. Audit-first architecture

Every processed record is written to an audit log with:

- original payload
- validation findings
- routing decision
- automation confidence
- recommended queue

This is important for compliance, debugging, and operational traceability.

### 4. Hybrid duplicate detection

The pipeline combines exact duplicate detection using business keys with fuzzy matching for similar customer names and equal amounts.

### 5. Data-quality reporting

The generated Markdown report summarizes recurring automation blockers. This shows process-improvement thinking, not only coding ability.

---

## Tech Stack

- Python 3.11
- FastAPI
- Pandas
- Pydantic v2
- SQLAlchemy
- pdfplumber
- RapidFuzz
- Jinja2
- Docker
- Pytest
- Ruff
- SQLite

---

## Project Structure

```text
app/
  api/                 FastAPI routes
  core/                settings and logging
  domain/              Pydantic domain models and API schemas
  extractors/          CSV/PDF extraction layer
  validation/          rule engine and duplicate detection
  rpa/                 exception routing and RPA output writer
  reporting/           data-quality report generation
  services/            end-to-end orchestration service
  storage/             audit database repository
scripts/
  run_sample_pipeline.py

data/
  samples/             sample input files
  output/              generated RPA outputs

tests/                 unit and integration tests
.github/workflows/     CI pipeline
```

---

## How to Run Locally

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate        # Windows PowerShell

pip install -e ".[dev]"
python scripts/run_sample_pipeline.py
```

Generated artifacts will appear in:

```text
data/output/
```

---

## Run the API

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

Upload a CSV or PDF through:

```text
POST /api/v1/pipeline/run
```

List previous runs:

```text
GET /api/v1/pipeline/runs
```

---

## Run with Docker

```bash
docker compose up --build
```

---

## Example Output Files

For every run, the pipeline generates:

| Artifact | Purpose |
|---|---|
| `*_automation_only.csv` | Clean records ready for RPA processing |
| `*_rpa_ready.csv` | Full record-level decision table |
| `*_exceptions.csv` | Validation failures for manual review |
| `*_audit.jsonl` | Record-level audit trail |
| `*_quality_report.md` | Data-quality and automation-readiness report |
| `*_summary.json` | Machine-readable run summary |


- Dockerized deployment
- tests and CI
- business-facing output artifacts
- clear separation between extraction, validation, routing, and reporting
