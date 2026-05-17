from decimal import Decimal

from pydantic import BaseModel


class CountrySalarySummary(BaseModel):
    """Aggregate salary stats per (country, currency).

    Grouped on the pair rather than country alone because a country may
    contain rows in multiple currencies (e.g. an MNC paying expats in USD
    inside India). Averaging across currencies would be meaningless."""

    country: str
    currency_code: str
    count: int
    min_salary: Decimal
    max_salary: Decimal
    avg_salary: Decimal


class JobTitleSalarySummary(BaseModel):
    job_title: str
    currency_code: str
    count: int
    min_salary: Decimal
    max_salary: Decimal
    avg_salary: Decimal


class CountryPercentiles(BaseModel):
    """Percentile spread for a country's active salaries. Averages hide
    distribution problems; percentiles surface them."""

    country: str
    currency_code: str
    count: int
    p25: Decimal
    p50: Decimal
    p75: Decimal
    p90: Decimal


class HeadcountBucket(BaseModel):
    name: str
    count: int


class HeadcountBreakdown(BaseModel):
    """Three slices the persona will reach for first: where are my people,
    which departments, and which roles dominate the org."""

    by_country: list[HeadcountBucket]
    by_department: list[HeadcountBucket]
    by_job_title: list[HeadcountBucket]
