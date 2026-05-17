from salary.repositories.employee import EmployeeRepository
from tests.factories import make_employee


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
