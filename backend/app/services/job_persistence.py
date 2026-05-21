# sincroniza jobs em memória com a tabela jobs (sqlite)
from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from backend.app.api.models import Job, JobStatus
from backend.app.database.connection import DatabaseConnection
from backend.app.database import crud


def persist_job(job: Job) -> None:
    session = DatabaseConnection.get_session()
    try:
        crud.JobCRUD.upsert(session, job)
    finally:
        session.close()


def job_from_record(row) -> Job:
    from backend.app.api.models import JobType

    jt = row.job_type
    try:
        job_type = JobType(jt)
    except ValueError:
        job_type = JobType.GENERATE_MODEL
    try:
        status = JobStatus(row.status)
    except ValueError:
        status = JobStatus.FAILED
    return Job(
        job_id=row.job_id,
        job_type=job_type,
        status=status,
        progress=int(row.progress or 0),
        created_at=row.created_at or datetime.now(),
        updated_at=row.updated_at or datetime.now(),
        output_files=list(row.output_files_json or []),
        logs=list(row.logs_json or []),
        error_message=row.error_message,
        metadata=dict(row.metadata_json or {}),
    )


def hydrate_jobs_store(
    jobs_store: Dict[str, Job],
    *,
    limit: int = 500,
) -> int:
    """carrega jobs da bd para o dict em memória; marca queued/running como failed."""
    session = DatabaseConnection.get_session()
    try:
        crud.JobCRUD.mark_stale_running_as_failed(session)
        rows = crud.JobCRUD.list_all(session, limit=limit)
        for row in rows:
            jobs_store[row.job_id] = job_from_record(row)
        return len(rows)
    finally:
        session.close()


def sync_job_in_store(jobs_store: Dict[str, Job], job_id: str) -> None:
    job = jobs_store.get(job_id)
    if job is not None:
        persist_job(job)
