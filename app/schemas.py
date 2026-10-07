from pydantic import BaseModel, EmailStr
from typing import List


class RecipientInput(BaseModel):
    name: str
    email: EmailStr


class CertificateRequest(BaseModel):
    event_name: str
    certificate_title: str
    issue_date: str
    recipients: List[RecipientInput]