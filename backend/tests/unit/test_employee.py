from datetime import date
from decimal import Decimal

from tests.factories import make_employee


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
    employee = make_employee(salary=Decimal("1234567.89"))

    assert isinstance(employee.salary, Decimal)
    assert employee.salary == Decimal("1234567.89")


def test_employee_holds_identification_fields():
    employee = make_employee(employee_id="EMP-00042", email="asha@example.com")

    assert employee.employee_id == "EMP-00042"
    assert employee.email == "asha@example.com"


def test_employee_holds_categorization_fields():
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
