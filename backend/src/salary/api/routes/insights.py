from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from salary.db import get_session
from salary.repositories.employee import EmployeeRepository
from salary.schemas.insights import (
    CountryPercentiles,
    CountrySalarySummary,
    HeadcountBreakdown,
    JobTitleSalarySummary,
)
from salary.services.insights_service import InsightsService

router = APIRouter(prefix="/insights", tags=["insights"])


def _service(session: Session = Depends(get_session)) -> InsightsService:
    return InsightsService(EmployeeRepository(session))


# Reusable Path validator: country codes are ISO 3166 alpha-2 (two uppercase).
Country = Path(..., pattern=r"^[A-Z]{2}$", description="ISO 3166 alpha-2")


@router.get("/by-country", response_model=list[CountrySalarySummary])
def by_country(service: InsightsService = Depends(_service)) -> list[CountrySalarySummary]:
    return service.country_summaries()


@router.get("/headcount", response_model=HeadcountBreakdown)
def headcount(service: InsightsService = Depends(_service)) -> HeadcountBreakdown:
    return service.headcount_breakdown()


@router.get(
    "/by-country/{country}/by-job-title",
    response_model=list[JobTitleSalarySummary],
)
def by_job_title_in_country(
    country: str = Country,
    service: InsightsService = Depends(_service),
) -> list[JobTitleSalarySummary]:
    return service.job_summaries_in_country(country)


@router.get(
    "/by-country/{country}/percentiles",
    response_model=list[CountryPercentiles],
)
def country_percentiles(
    country: str = Country,
    service: InsightsService = Depends(_service),
) -> list[CountryPercentiles]:
    return service.country_percentile_summaries(country)
