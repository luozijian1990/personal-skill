import uuid


JOBS: dict[str, dict[str, object]] = {}


def enqueue(targets: list[str]) -> str:
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"targets": targets, "status": "running"}
    return job_id


def get_job(job_id: str) -> dict[str, object] | None:
    return JOBS.get(job_id)
