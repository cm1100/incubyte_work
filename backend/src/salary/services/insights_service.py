import statistics
from decimal import Decimal

from salary.repositories.employee import EmployeeRepository
from salary.schemas.insights import (
    CountryPercentiles,
    CountrySalarySummary,
    HeadcountBreakdown,
    HeadcountBucket,
    JobTitleSalarySummary,
)


def _money(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


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

    def job_summaries_in_country(self, country: str) -> list[JobTitleSalarySummary]:
        rows = self.repo.summarize_jobs_in_country(country, status=self._ACTIVE_ONLY)
        return [JobTitleSalarySummary(**row) for row in rows]

    def headcount_breakdown(self, limit: int = 20) -> HeadcountBreakdown:
        def _buckets(dimension: str) -> list[HeadcountBucket]:
            rows = self.repo.headcounts_by(
                dimension, status=self._ACTIVE_ONLY, limit=limit
            )
            return [HeadcountBucket(**row) for row in rows]

        return HeadcountBreakdown(
            by_country=_buckets("country"),
            by_department=_buckets("department"),
            by_job_title=_buckets("job_title"),
        )

    def country_percentile_summaries(self, country: str) -> list[CountryPercentiles]:
        distributions = self.repo.salaries_by_currency_in_country(
            country, status=self._ACTIVE_ONLY
        )
        out: list[CountryPercentiles] = []
        for currency, salaries in distributions.items():
            n = len(salaries)
            if n == 1:
                # Single data point: no spread to compute. Collapse all
                # four percentiles to that value rather than raising; the
                # client gets a coherent shape every time.
                p25 = p50 = p75 = p90 = salaries[0]
            else:
                # 'inclusive' matches numpy/pandas; the default 'exclusive'
                # extrapolates beyond [min, max] which is nonsensical for
                # bounded salary data.
                q4 = statistics.quantiles(salaries, n=4, method="inclusive")
                q10 = statistics.quantiles(salaries, n=10, method="inclusive")
                p25, p50, p75 = q4
                p90 = q10[8]  # index 8 = the 9th of 9 cuts = p90
            out.append(
                CountryPercentiles(
                    country=country,
                    currency_code=currency,
                    count=n,
                    p25=_money(p25),
                    p50=_money(p50),
                    p75=_money(p75),
                    p90=_money(p90),
                )
            )
        return out
