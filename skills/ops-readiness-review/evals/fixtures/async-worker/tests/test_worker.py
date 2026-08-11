from api import create_inspection
from worker import get_job


def test_create_inspection_returns_job_id():
    result = create_inspection(["fixture-host"])
    assert result["job_id"]


def test_get_job_returns_running_state():
    result = create_inspection(["fixture-host"])
    assert get_job(result["job_id"])["status"] == "running"
