from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from salary.db import get_session
from salary.models.employee import Employee
from salary.repositories.employee import EmployeeRepository
from salary.schemas.employee import EmployeeCreate, EmployeePage, EmployeeRead

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


@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(
    employee_id: str,
    session: Session = Depends(get_session),
) -> Employee:
    repo = EmployeeRepository(session)
    employee = repo.get_by_employee_id(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="employee not found")
    return employee


@router.get("", response_model=EmployeePage)
def list_employees(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = Query(None, min_length=1, max_length=100),
    session: Session = Depends(get_session),
) -> EmployeePage:
    repo = EmployeeRepository(session)
    items, total = repo.list(offset=offset, limit=limit, search=search)
    return EmployeePage(
        items=[EmployeeRead.model_validate(i) for i in items],
        total=total,
        offset=offset,
        limit=limit,
    )
