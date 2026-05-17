from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from salary.models.employee import Employee


class EmployeeRepository:
    """Data access for Employee. SQL-only; no business rules.

    The repo does not commit — transaction boundaries belong to the caller
    (the FastAPI dependency in production, the test fixture in tests).
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, employee: Employee) -> Employee:
        self.session.add(employee)
        self.session.flush()
        self.session.refresh(employee)
        return employee

    def get_by_id(self, employee_id: int) -> Employee | None:
        return self.session.get(Employee, employee_id)
