from sqlalchemy.orm import Mapped, mapped_column

from salary.db import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
