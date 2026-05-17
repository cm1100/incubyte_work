# Lazy annotation evaluation so `list[dict]` in method signatures doesn't
# break on Python 3.12, where the `def list(self, ...)` method below shadows
# the `list` builtin in the class-body namespace by the time later
# annotations are eagerly evaluated. PEP 649 makes this a no-op on 3.14+,
# where annotations are already deferred. Local dev runs 3.14, prod runs
# 3.12 in the container — caught when the container kept restart-looping.
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from salary.models.employee import Employee


def _money(value) -> Decimal:
    """Coerce DB aggregate output to Decimal with money precision.
    SQLite returns NUMERIC aggregates as Decimal already, but some drivers
    return float; str() bridges either case without precision loss."""
    return Decimal(str(value)).quantize(Decimal("0.01"))


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

    # ---------- aggregations for insights ----------

    def summarize_by_country(self, status: str = "active") -> list[dict]:
        """Per (country, currency) aggregates over rows matching status.
        SUM + count divided in Python preserves Decimal precision; SQL
        AVG would coerce to float on SQLite."""
        stmt = (
            select(
                Employee.country,
                Employee.currency_code,
                func.count().label("count"),
                func.min(Employee.salary).label("min_salary"),
                func.max(Employee.salary).label("max_salary"),
                func.sum(Employee.salary).label("sum_salary"),
            )
            .where(Employee.status == status)
            .group_by(Employee.country, Employee.currency_code)
            .order_by(Employee.country, Employee.currency_code)
        )
        return [
            {
                "country": r["country"],
                "currency_code": r["currency_code"],
                "count": r["count"],
                "min_salary": _money(r["min_salary"]),
                "max_salary": _money(r["max_salary"]),
                "avg_salary": _money(Decimal(str(r["sum_salary"])) / r["count"]),
            }
            for r in self.session.execute(stmt).mappings().all()
        ]

    _HEADCOUNT_COLUMNS = None  # populated lazily to avoid Employee circular ref at class-body time

    @classmethod
    def _headcount_column(cls, dimension: str):
        if cls._HEADCOUNT_COLUMNS is None:
            cls._HEADCOUNT_COLUMNS = {
                "country": Employee.country,
                "department": Employee.department,
                "job_title": Employee.job_title,
            }
        try:
            return cls._HEADCOUNT_COLUMNS[dimension]
        except KeyError as e:
            raise ValueError(f"unsupported headcount dimension: {dimension}") from e

    def headcounts_by(
        self, dimension: str, status: str = "active", limit: int = 20
    ) -> list[dict]:
        """COUNT(*) GROUP BY <dimension>, sorted by count desc, top N.
        dimension must be one of: country, department, job_title."""
        column = self._headcount_column(dimension)
        stmt = (
            select(column.label("name"), func.count().label("count"))
            .where(Employee.status == status)
            .group_by(column)
            .order_by(func.count().desc(), column)
            .limit(limit)
        )
        return [
            {"name": r["name"], "count": r["count"]}
            for r in self.session.execute(stmt).mappings().all()
        ]

    def salaries_by_currency_in_country(
        self, country: str, status: str = "active"
    ) -> dict[str, list[Decimal]]:
        """Returns {currency_code: ASC-sorted list[Decimal]} so the service
        can run percentile math without re-sorting."""
        stmt = (
            select(Employee.currency_code, Employee.salary)
            .where(Employee.country == country, Employee.status == status)
            .order_by(Employee.currency_code, Employee.salary)
        )
        result: dict[str, list[Decimal]] = {}
        for currency, salary in self.session.execute(stmt).all():
            result.setdefault(currency, []).append(_money(salary))
        return result

    def summarize_jobs_in_country(
        self, country: str, status: str = "active"
    ) -> list[dict]:
        """Per (job_title, currency_code) aggregates inside one country.
        Uses the composite (country, job_title) index for the WHERE +
        GROUP BY."""
        stmt = (
            select(
                Employee.job_title,
                Employee.currency_code,
                func.count().label("count"),
                func.min(Employee.salary).label("min_salary"),
                func.max(Employee.salary).label("max_salary"),
                func.sum(Employee.salary).label("sum_salary"),
            )
            .where(Employee.country == country, Employee.status == status)
            .group_by(Employee.job_title, Employee.currency_code)
            .order_by(Employee.job_title, Employee.currency_code)
        )
        return [
            {
                "job_title": r["job_title"],
                "currency_code": r["currency_code"],
                "count": r["count"],
                "min_salary": _money(r["min_salary"]),
                "max_salary": _money(r["max_salary"]),
                "avg_salary": _money(Decimal(str(r["sum_salary"])) / r["count"]),
            }
            for r in self.session.execute(stmt).mappings().all()
        ]
