FROM python:3.12-slim AS base

# python:3.12-slim ships for both linux/amd64 and linux/arm64, so the
# same Dockerfile builds on a t4g.nano (Graviton ARM) and a Mac.

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy everything before pip install — src-layout means setuptools needs
# src/ visible at install time to discover packages. We get layer-cache
# benefits from the base image and ENV/WORKDIR layers; deps re-resolve
# only when project files change (which is fine at this scale).
COPY . .

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "salary.main:app", "--host", "0.0.0.0", "--port", "8000"]
