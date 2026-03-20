# RoBe Backend

Modular monolith backend using FastAPI, async SQLAlchemy (PostgreSQL), Redis, Celery, and Docker.

## Requirements

- Python `3.12+`
- Docker (optional, for containerized runs)

## Configuration

Copy `.env.example` to `.env` and update values as needed.

## Run (local)

### With Docker

```sh
make up
```

API:
- `GET http://localhost:8000/health`
- `GET http://localhost:8000/api/v1/health`

### Without Docker

```sh
pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Notes

- This is an infrastructure-only scaffold. Business modules (auth/pets/chat/etc.) are intentionally not implemented yet.

