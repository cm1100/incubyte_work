from decimal import Decimal

from salary.repositories.employee import EmployeeRepository
from tests.factories import make_employee


def test_summarize_by_country_aggregates_active_employees(session):
    repo = EmployeeRepository(session)
    # 3 active IN/INR with salaries 1000/2000/3000 → avg=2000, sum=6000.
    for i, sal in enumerate([1000, 2000, 3000]):
        repo.create(
            make_employee(
                employee_id=f"EMP-IN-{i}",
                email=f"in{i}@x.com",
                country="IN",
                currency_code="INR",
                salary=Decimal(str(sal)),
            )
        )
    # 2 active US/USD with salaries 50000/70000 → avg=60000.
    for i, sal in enumerate([50000, 70000]):
        repo.create(
            make_employee(
                employee_id=f"EMP-US-{i}",
                email=f"us{i}@x.com",
                country="US",
                currency_code="USD",
                salary=Decimal(str(sal)),
            )
        )
    # 1 terminated IN/INR — must NOT be in the active aggregate.
    repo.create(
        make_employee(
            employee_id="EMP-IN-T",
            email="int@x.com",
            country="IN",
            currency_code="INR",
            salary=Decimal("9999"),
            status="terminated",
        )
    )

    rows = repo.summarize_by_country(status="active")
    by_country = {(r["country"], r["currency_code"]): r for r in rows}

    in_row = by_country[("IN", "INR")]
    assert in_row["count"] == 3
    assert in_row["min_salary"] == Decimal("1000.00")
    assert in_row["max_salary"] == Decimal("3000.00")
    assert in_row["avg_salary"] == Decimal("2000.00")

    us_row = by_country[("US", "USD")]
    assert us_row["count"] == 2
    assert us_row["avg_salary"] == Decimal("60000.00")


def test_summarize_by_country_returns_empty_when_no_rows(session):
    repo = EmployeeRepository(session)

    assert repo.summarize_by_country(status="active") == []
