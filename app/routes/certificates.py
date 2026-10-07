from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Recipient

router = APIRouter(
    prefix="/certificates",
    tags=["Certificates"]
)


@router.get("/{recipient_id}")
def download_certificate(
    recipient_id: int,
    db: Session = Depends(get_db)
):
    recipient = db.query(Recipient).filter(
        Recipient.id == recipient_id
    ).first()

    if not recipient:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    if recipient.certificate_status != "success":
        raise HTTPException(
            status_code=404,
            detail="Certificate was not generated successfully"
        )

    if not recipient.certificate_path:
        raise HTTPException(
            status_code=404,
            detail="Certificate file not available"
        )

    file_path = Path(recipient.certificate_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Certificate file does not exist"
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path.name
    )