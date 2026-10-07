from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# Folder where generated certificates are stored
CERTIFICATE_DIR = Path("certificates")
CERTIFICATE_DIR.mkdir(exist_ok=True)


def generate_certificate(
    recipient_name: str,
    event_name: str,
    certificate_title: str,
    issue_date: str,
    certificate_id: int
) -> str:
    """
    Generate one certificate PDF and return its file path.
    """

    file_path = CERTIFICATE_DIR / f"certificate_{certificate_id}.pdf"

    pdf = canvas.Canvas(str(file_path), pagesize=A4)

    width, height = A4

    # Certificate title
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawCentredString(
        width / 2,
        height - 150,
        certificate_title
    )

    # Main text
    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        width / 2,
        height - 220,
        "This certificate is proudly presented to"
    )

    # Recipient name
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(
        width / 2,
        height - 280,
        recipient_name
    )

    # Event information
    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        width / 2,
        height - 340,
        f"for participating in {event_name}"
    )

    # Date
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(
        width / 2,
        height - 400,
        f"Date: {issue_date}"
    )

    pdf.save()

    return str(file_path)