from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Recipient
import app.services.certificate_generator as certificate_generator
import app.routes.jobs as jobs_module


# Test database
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_database(tmp_path, monkeypatch):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(
        certificate_generator,
        "CERTIFICATE_DIR",
        tmp_path
    )

    yield


def sample_request():
    return {
        "event_name": "Python Workshop",
        "certificate_title": "Certificate of Participation",
        "issue_date": "2026-10-07",
        "recipients": [
            {
                "name": "Anu",
                "email": "anu@example.com"
            },
            {
                "name": "Ravi",
                "email": "ravi@example.com"
            }
        ]
    }


def test_create_generation_job():
    response = client.post(
        "/jobs/",
        json=sample_request()
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_recipients"] == 2
    assert data["successful_count"] == 2
    assert data["failed_count"] == 0
    assert data["status"] == "completed"


def test_input_validation():
    data = sample_request()

    data["recipients"][0]["email"] = "invalid-email"

    response = client.post(
        "/jobs/",
        json=data
    )

    assert response.status_code == 422


def test_certificate_generation(tmp_path):
    response = client.post(
        "/jobs/",
        json=sample_request()
    )

    assert response.status_code == 200

    files = list(Path(tmp_path).glob("*.pdf"))

    assert len(files) == 2


def test_job_status():
    response = client.post(
        "/jobs/",
        json=sample_request()
    )

    job_id = response.json()["job_id"]

    status_response = client.get(
        f"/jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["job_id"] == job_id
    assert data["status"] == "completed"
    assert data["successful_count"] == 2
    assert data["failed_count"] == 0


def test_individual_certificate_failure(monkeypatch):
    original_function = jobs_module.generate_certificate

    def failing_generator(
        recipient_name,
        event_name,
        certificate_title,
        issue_date,
        certificate_id
    ):
        if recipient_name == "Ravi":
            raise Exception("Certificate generation failed")

        return original_function(
            recipient_name,
            event_name,
            certificate_title,
            issue_date,
            certificate_id
        )

    monkeypatch.setattr(
        jobs_module,
        "generate_certificate",
        failing_generator
    )

    response = client.post(
        "/jobs/",
        json=sample_request()
    )

    assert response.status_code == 200

    data = response.json()

    assert data["successful_count"] == 1
    assert data["failed_count"] == 1
    assert data["status"] == "completed_with_errors"


def test_retrieve_generated_certificate():
    response = client.post(
        "/jobs/",
        json=sample_request()
    )

    assert response.status_code == 200

    db = TestingSessionLocal()

    recipient = db.query(Recipient).first()

    db.close()

    download_response = client.get(
        f"/certificates/{recipient.id}"
    )

    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"