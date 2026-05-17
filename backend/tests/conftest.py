"""Shared fixtures: engine + session against in-memory SQLite. Both
integration (repo) and API tests build on these."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from salary import models  # noqa: F401 — registers tables on Base.metadata
from salary.db import Base
from salary.main import app


@pytest.fixture
def engine():
    # check_same_thread=False + StaticPool so the in-memory DB is shared
    # across threads (FastAPI TestClient dispatches sync handlers to a
    # worker thread). Each test still gets its own fresh DB.
    eng = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def session(engine) -> Session:
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    with SessionLocal() as s:
        yield s


@pytest.fixture
def client() -> TestClient:
    """Health/smoke client only — does not touch the DB. API tests build
    a separate client in tests/api/conftest.py that overrides get_session."""
    return TestClient(app)
