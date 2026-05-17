from salary.repositories.employee import EmployeeRepository
from salary.schemas.insights import CountrySalarySummary


class InsightsService:
    """Applies insight-wide product rules that shouldn't leak into the
    repo (which is SQL-only) or the route (which is transport-only).

    Today the only rule is the active-only status filter — terminated
    employees skew the math and are excluded by default. As more rules
    accrue (top-N caps, include_inactive override, etc.) they land here."""

    _ACTIVE_ONLY = "active"

    def __init__(self, repo: EmployeeRepository) -> None:
        self.repo = repo

    def country_summaries(self) -> list[CountrySalarySummary]:
        rows = self.repo.summarize_by_country(status=self._ACTIVE_ONLY)
        return [CountrySalarySummary(**row) for row in rows]
