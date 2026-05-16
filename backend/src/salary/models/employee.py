from sqlalchemy.orm import Mapped, mapped_column

from salary.db import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    first_name: Mapped[str]
    last_name: Mapped[str]
    status: Mapped[str] = mapped_column(default="active")
    employment_type: Mapped[str] = mapped_column(default="full_time")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
