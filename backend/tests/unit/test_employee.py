from datetime import date
from decimal import Decimal

from salary.models.employee import Employee


def make_employee(**overrides) -> Employee:
    """Construct a minimal-valid Employee. Tests override only the fields they assert on,
    so adding new required fields elsewhere does not ripple through unrelated tests."""
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
    employee = make_employee(salary=Decimal("1234567.89"))

    assert isinstance(employee.salary, Decimal)
    assert employee.salary == Decimal("1234567.89")


def test_employee_holds_identification_fields():
    """employee_id is the human-readable handle; email is the unique
    contact key. Both are kept on the model so reports and dedup checks
    can use either."""
    employee = make_employee(employee_id="EMP-00042", email="asha@example.com")

    assert employee.employee_id == "EMP-00042"
    assert employee.email == "asha@example.com"


def test_employee_holds_categorization_fields():
    """country / job_title / department are the slices an HR manager
    reaches for first. They must be on the model directly, not joined
    in from a lookup table at insight time."""
    employee = make_employee(
        country="IN",
        job_title="Senior Engineer",
        department="Engineering",
    )

    assert employee.country == "IN"
    assert employee.job_title == "Senior Engineer"
    assert employee.department == "Engineering"


def test_employee_holds_hire_date_as_date_not_string():
    employee = make_employee(hire_date=date(2023, 1, 15))

    assert isinstance(employee.hire_date, date)
    assert employee.hire_date == date(2023, 1, 15)
