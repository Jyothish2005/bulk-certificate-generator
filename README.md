# Bulk Certificate Generator API

A FastAPI-based backend API for generating certificates in bulk.

## Features

- Create bulk certificate generation jobs
- Validate recipient information
- Generate PDF certificates
- Track generation status
- Handle individual certificate failures
- Retrieve generated certificates
- Store job and recipient information in SQLite
- Automated tests

## Technology Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- ReportLab
- Pydantic
- Pytest

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── database.py
│   ├── schemas.py
│   └── main.py
│
├── certificates/
├── tests/
│   └── test_api.py
│
├── requirements.txt
├── README.md
└── .gitignore