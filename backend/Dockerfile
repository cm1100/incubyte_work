FROM python:3.12-slim AS base

# python:3.12-slim ships for both linux/amd64 and linux/arm64, so the
# same Dockerfile builds on a t4g.nano (Graviton ARM) and a Mac.

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install deps first as a separate layer so source changes don't bust
# the pip install cache.
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# App code
COPY src/ src/
COPY alembic.ini ./
COPY alembic/ alembic/
COPY seed_data/ seed_data/

# SQLite file lives on a bind-mounted host volume (see docker-compose.yml)
# so it survives container restarts. Path is created at runtime by Compose.

EXPOSE 8000

CMD ["uvicorn", "salary.main:app", "--host", "0.0.0.0", "--port", "8000"]
