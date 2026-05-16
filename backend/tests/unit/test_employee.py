from salary.models.employee import Employee


def test_full_name_combines_first_and_last_name():
    employee = Employee(first_name="Asha", last_name="Sharma")

    assert employee.full_name == "Asha Sharma"


def test_status_defaults_to_active():
    employee = Employee(first_name="Asha", last_name="Sharma")

    assert employee.status == "active"


def test_employment_type_defaults_to_full_time():
    employee = Employee(first_name="Asha", last_name="Sharma")

    assert employee.employment_type == "full_time"
