# Salary Management — Backend

FastAPI + SQLAlchemy 2.0 + SQLite.

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run tests

```bash
pytest
```

## Run dev server

```bash
uvicorn salary.main:app --reload
```

Visit `http://localhost:8000/docs` for the OpenAPI UI.
