from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from salary.db import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    first_name: Mapped[str]
    last_name: Mapped[str]
    salary: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency_code: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(default="active")
    employment_type: Mapped[str] = mapped_column(default="full_time")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
