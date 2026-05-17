"""Test factories. Each call returns a fresh minimal-valid object;
tests override only the fields they assert on."""

from datetime import date
from decimal import Decimal

from salary.models.employee import Employee


def make_employee(**overrides) -> Employee:
    defaults = dict(
        employee_id="EMP-00001",
        first_name="Asha",
        last_name="Sharma",
        email="asha@example.com",
        job_title="Engineer",
        department="Engineering",
        country="IN",
        salary=Decimal("1500000.00"),
        currency_code="INR",
        hire_date=date(2023, 1, 15),
    )
    defaults.update(overrides)
    return Employee(**defaults)
