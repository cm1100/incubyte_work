from salary.models.employee import Employee


def test_full_name_combines_first_and_last_name():
    employee = Employee(first_name="Asha", last_name="Sharma")

    assert employee.full_name == "Asha Sharma"
