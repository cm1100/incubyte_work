from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from salary.db import get_session
from salary.repositories.employee import EmployeeRepository
from salary.schemas.insights import CountrySalarySummary
from salary.services.insights_service import InsightsService

router = APIRouter(prefix="/insights", tags=["insights"])


def _service(session: Session = Depends(get_session)) -> InsightsService:
    return InsightsService(EmployeeRepository(session))


@router.get("/by-country", response_model=list[CountrySalarySummary])
def by_country(service: InsightsService = Depends(_service)) -> list[CountrySalarySummary]:
    return service.country_summaries()
