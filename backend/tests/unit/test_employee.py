from decimal import Decimal

from salary.models.employee import Employee


def make_employee(**overrides) -> Employee:
    """Construct a minimal-valid Employee. Tests override only the fields they assert on,
    so adding new required fields elsewhere does not ripple through unrelated tests."""
    defaults = dict(
        first_name="Asha",
        last_name="Sharma",
        salary=Decimal("1500000.00"),
        currency_code="INR",
    )
    defaults.update(overrides)
    return Employee(**defaults)


def test_full_name_combines_first_and_last_name():
    employee = make_employee(first_name="Asha", last_name="Sharma")

    assert employee.full_name == "Asha Sharma"


def test_status_defaults_to_active():
    employee = make_employee()

    assert employee.status == "active"


def test_employment_type_defaults_to_full_time():
    employee = make_employee()

    assert employee.employment_type == "full_time"


def test_salary_is_stored_as_decimal_not_float():
    """Salary must stay a Decimal in memory; float would risk silent
    rounding drift on aggregations later."""
    employee = make_employee(salary=Decimal("1234567.89"), currency_code="INR")

    assert isinstance(employee.salary, Decimal)
    assert employee.salary == Decimal("1234567.89")
    assert employee.currency_code == "INR"
