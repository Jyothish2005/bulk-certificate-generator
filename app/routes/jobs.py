from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GenerationJob, Recipient
from app.schemas import CertificateRequest
from app.services.certificate_generator import generate_certificate

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.post("/")
def create_generation_job(
    request: CertificateRequest,
    db: Session = Depends(get_db)
):
    # Create a new job
    job = GenerationJob(
        status="processing",
        total_recipients=len(request.recipients)
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Add all recipients
    recipients = []

    for recipient_data in request.recipients:
        recipient = Recipient(
            job_id=job.id,
            name=recipient_data.name,
            email=recipient_data.email,
            certificate_status="pending"
        )

        db.add(recipient)
        recipients.append(recipient)

    # Generate IDs for recipients before creating certificates
    db.flush()

    successful_count = 0
    failed_count = 0

    # Generate certificate for each recipient
    for recipient in recipients:
        try:
            file_path = generate_certificate(
                recipient_name=recipient.name,
                event_name=request.event_name,
                certificate_title=request.certificate_title,
                issue_date=request.issue_date,
                certificate_id=recipient.id
            )

            recipient.certificate_status = "success"
            recipient.certificate_path = file_path

            successful_count += 1

        except Exception as error:
            recipient.certificate_status = "failed"
            recipient.error_message = str(error)

            failed_count += 1

    # Update job results
    job.successful_count = successful_count
    job.failed_count = failed_count

    if failed_count == 0:
        job.status = "completed"
    elif successful_count == 0:
        job.status = "failed"
    else:
        job.status = "completed_with_errors"

    db.commit()

    return {
        "job_id": job.id,
        "status": job.status,
        "total_recipients": job.total_recipients,
        "successful_count": job.successful_count,
        "failed_count": job.failed_count,
        "message": "Certificate generation completed"
    }

@router.get("/{job_id}")
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id
    ).first()

    if not job:
        return {
            "error": "Job not found"
        }

    return {
        "job_id": job.id,
        "status": job.status,
        "total_recipients": job.total_recipients,
        "successful_count": job.successful_count,
        "failed_count": job.failed_count,
        "created_at": job.created_at
    }