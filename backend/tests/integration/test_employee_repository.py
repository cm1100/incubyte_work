from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from salary.repositories.employee import EmployeeRepository
from tests.factories import make_employee


# ---------- create / get_by_id ----------


def test_create_persists_employee_and_assigns_id(session):
    repo = EmployeeRepository(session)

    employee = repo.create(make_employee())

    assert employee.id is not None
    assert employee.created_at is not None


def test_get_by_id_returns_existing_employee(session):
    repo = EmployeeRepository(session)
    created = repo.create(make_employee(email="asha@example.com"))

    found = repo.get_by_id(created.id)

    assert found is not None
    assert found.email == "asha@example.com"


def test_get_by_id_returns_none_when_missing(session):
    repo = EmployeeRepository(session)

    assert repo.get_by_id(99999) is None


# ---------- list (pagination + search) ----------


def _seed(session, count: int) -> EmployeeRepository:
    repo = EmployeeRepository(session)
    for i in range(count):
        repo.create(
            make_employee(
                employee_id=f"EMP-{i:05d}",
                email=f"user{i}@example.com",
                first_name=f"First{i}",
                last_name=f"Last{i}",
            )
        )
    return repo


def test_list_returns_empty_page_and_zero_total_when_no_rows(session):
    """Empty store must still produce a well-formed (items, total) pair —
    the UI relies on this to render 'no results' instead of crashing."""
    repo = EmployeeRepository(session)

    items, total = repo.list(offset=0, limit=10)

    assert items == []
    assert total == 0


def test_list_returns_items_and_total_count(session):
    repo = _seed(session, count=5)

    items, total = repo.list(offset=0, limit=10)

    assert total == 5
    assert len(items) == 5


def test_list_paginates_via_offset_and_limit(session):
    repo = _seed(session, count=12)

    page_one, total = repo.list(offset=0, limit=5)
    page_three, _ = repo.list(offset=10, limit=5)

    assert total == 12
    assert len(page_one) == 5
    assert len(page_three) == 2  # remainder


def test_list_filters_by_search_against_name_and_email(session):
    repo = _seed(session, count=3)
    repo.create(make_employee(employee_id="EMP-NEEDLE", email="needle@example.com",
                              first_name="Needle", last_name="Findme"))

    items, total = repo.list(offset=0, limit=10, search="needle")

    assert total == 1
    assert items[0].employee_id == "EMP-NEEDLE"


# ---------- update / delete ----------


def test_update_changes_fields_and_returns_updated(session):
    repo = EmployeeRepository(session)
    created = repo.create(make_employee(job_title="Engineer"))

    updated = repo.update(created.id, job_title="Senior Engineer")

    assert updated is not None
    assert updated.job_title == "Senior Engineer"


def test_update_returns_none_when_missing(session):
    repo = EmployeeRepository(session)

    assert repo.update(99999, job_title="x") is None


def test_delete_removes_employee_and_returns_true(session):
    repo = EmployeeRepository(session)
    created = repo.create(make_employee())

    assert repo.delete(created.id) is True
    assert repo.get_by_id(created.id) is None


def test_delete_returns_false_when_missing(session):
    repo = EmployeeRepository(session)

    assert repo.delete(99999) is False


# ---------- integrity contracts ----------


def test_duplicate_email_raises_integrity_error(session):
    repo = EmployeeRepository(session)
    repo.create(make_employee(employee_id="EMP-A", email="dup@example.com"))

    with pytest.raises(IntegrityError):
        repo.create(make_employee(employee_id="EMP-B", email="dup@example.com"))


def test_negative_salary_is_rejected_by_db_constraint(session):
    """Defence in depth. The Pydantic schema will reject this at the API
    boundary, but the seed script writes via bulk insert without that
    layer — the DB has to enforce."""
    repo = EmployeeRepository(session)

    with pytest.raises(IntegrityError):
        repo.create(make_employee(salary=Decimal("-1.00")))
