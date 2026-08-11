from worker import enqueue


def create_inspection(targets: list[str]) -> dict[str, str]:
    job_id = enqueue(targets)
    return {"job_id": job_id, "status": "accepted"}
