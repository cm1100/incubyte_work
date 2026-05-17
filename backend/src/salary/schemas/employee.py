from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

EmploymentType = Literal["full_time", "part_time", "contract"]
EmployeeStatus = Literal["active", "on_leave", "terminated"]


class EmployeeCreate(BaseModel):
    """POST /employees request body. Every field validated here so the
    repository/DB layer never sees garbage."""

    employee_id: str = Field(min_length=3, max_length=16)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    job_title: str = Field(min_length=1, max_length=100)
    department: str = Field(min_length=1, max_length=100)
    country: str = Field(pattern=r"^[A-Z]{2}$", description="ISO 3166 alpha-2")
    salary: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    currency_code: str = Field(pattern=r"^[A-Z]{3}$", description="ISO 4217")
    hire_date: date
    status: EmployeeStatus = "active"
    employment_type: EmploymentType = "full_time"


class EmployeeUpdate(BaseModel):
    """PATCH /employees/{id}. All fields optional; only provided keys
    are applied (model_dump(exclude_unset=True) at the route)."""

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    job_title: str | None = Field(default=None, min_length=1, max_length=100)
    department: str | None = Field(default=None, min_length=1, max_length=100)
    country: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")
    salary: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    currency_code: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")
    hire_date: date | None = None
    status: EmployeeStatus | None = None
    employment_type: EmploymentType | None = None


class EmployeeRead(BaseModel):
    """Response shape for a single employee. from_attributes lets FastAPI
    serialize directly from the SQLAlchemy model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    job_title: str
    department: str
    country: str
    salary: Decimal
    currency_code: str
    hire_date: date
    status: str
    employment_type: str
    created_at: datetime
    updated_at: datetime


class EmployeePage(BaseModel):
    """Pagination envelope so the UI can render 'showing N of M' in one
    response."""

    items: list[EmployeeRead]
    total: int
    offset: int
    limit: int
