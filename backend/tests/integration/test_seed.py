from sqlalchemy import func, select

from salary.models.employee import Employee
from salary.seed import bulk_insert, generate_employee_rows


# ---------- pure generation (no DB) ----------


def test_generate_returns_requested_count():
    assert len(generate_employee_rows(count=100, seed=42)) == 100


def test_generate_is_deterministic_for_same_seed():
    a = generate_employee_rows(count=50, seed=42)
    b = generate_employee_rows(count=50, seed=42)

    assert a == b


def test_generate_each_row_has_all_required_fields():
    required = {
        "employee_id", "first_name", "last_name", "email",
        "job_title", "department", "country", "salary",
        "currency_code", "hire_date", "status", "employment_type",
    }
    for row in generate_employee_rows(count=5, seed=42):
        assert required.issubset(row.keys())


def test_generate_emails_are_unique_at_10k():
    rows = generate_employee_rows(count=10_000, seed=42)

    assert len({r["email"] for r in rows}) == 10_000


def test_generate_employee_ids_are_unique_at_10k():
    rows = generate_employee_rows(count=10_000, seed=42)

    assert len({r["employee_id"] for r in rows}) == 10_000


def test_generate_distributes_across_multiple_countries():
    rows = generate_employee_rows(count=1_000, seed=42)

    assert len({r["country"] for r in rows}) >= 5


# ---------- bulk insert into a session ----------


def test_bulk_insert_persists_all_rows(session):
    rows = generate_employee_rows(count=50, seed=42)

    bulk_insert(session, rows)
    session.commit()

    count = session.scalar(select(func.count()).select_from(Employee))
    assert count == 50
