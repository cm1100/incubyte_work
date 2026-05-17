from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from salary.db import get_session
from salary.models.employee import Employee
from salary.repositories.employee import EmployeeRepository
from salary.schemas.employee import EmployeeCreate, EmployeeRead

# No service layer for plain CRUD — the route is thin and the repo is
# SQL-only. A service module appears in Phase 3 when insights need real
# business rules (status filters, currency handling).
router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    session: Session = Depends(get_session),
) -> Employee:
    repo = EmployeeRepository(session)
    employee = Employee(**payload.model_dump())
    return repo.create(employee)
