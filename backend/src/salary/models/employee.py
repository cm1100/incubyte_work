from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from salary.db import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    # Identification
    employee_id: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)

    # Name
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))

    # Categorization (the slices insights care about)
    job_title: Mapped[str] = mapped_column(String(100), index=True)
    department: Mapped[str] = mapped_column(String(100), index=True)
    country: Mapped[str] = mapped_column(String(2), index=True)  # ISO 3166 alpha-2

    # Compensation
    salary: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency_code: Mapped[str] = mapped_column(String(3))  # ISO 4217

    # Employment
    hire_date: Mapped[date]
    status: Mapped[str] = mapped_column(String(16), default="active")
    employment_type: Mapped[str] = mapped_column(String(16), default="full_time")

    # Audit timestamps — server-side defaults so they're correct regardless of caller.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        init=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        init=False,
    )

    # Composite index for the per-country-per-job-title insight query.
    __table_args__ = (Index("ix_employees_country_job_title", "country", "job_title"),)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
