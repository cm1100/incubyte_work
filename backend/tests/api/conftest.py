"""API-test client wired to the in-memory session.

The production `get_session` dependency is overridden so every request in
a test hits the per-test in-memory SQLite, not the prod sqlite file."""

import pytest
from fastapi.testclient import TestClient

from salary.db import get_session
from salary.main import app


@pytest.fixture
def api_client(session) -> TestClient:
    def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
