FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir --upgrade pip

COPY app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini

COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir .

CMD ["celery", "-A", "app.core.celery_app:celery_app", "worker", "--loglevel=INFO"]
