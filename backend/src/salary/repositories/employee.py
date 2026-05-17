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

    def get_by_employee_id(self, employee_id: str) -> Employee | None:
        """Lookup by the human-readable EMP-XXXXX key. Used by the API
        URLs (/employees/EMP-00042) since that's what HR navigates with."""
        return self.session.scalar(
            select(Employee).where(Employee.employee_id == employee_id)
        )

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        search: str | None = None,
    ) -> tuple[list[Employee], int]:
        """Return (page, total). Total is the count *after* filtering so
        the UI can render 'showing 50 of 327'."""
        stmt = select(Employee)
        count_stmt = select(func.count()).select_from(Employee)

        if search:
            like = f"%{search}%"
            condition = or_(
                Employee.first_name.ilike(like),
                Employee.last_name.ilike(like),
                Employee.email.ilike(like),
                Employee.employee_id.ilike(like),
            )
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        total = self.session.scalar(count_stmt) or 0
        items = list(
            self.session.scalars(stmt.order_by(Employee.id).offset(offset).limit(limit))
        )
        return items, total

    def update(self, employee_id: int, **fields) -> Employee | None:
        employee = self.get_by_id(employee_id)
        if employee is None:
            return None
        for key, value in fields.items():
            setattr(employee, key, value)
        self.session.flush()
        self.session.refresh(employee)
        return employee

    def delete(self, employee_id: int) -> bool:
        employee = self.get_by_id(employee_id)
        if employee is None:
            return False
        self.session.delete(employee)
        self.session.flush()
        return True
