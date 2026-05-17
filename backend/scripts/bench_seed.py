"""Benchmark naive ORM add vs SQLAlchemy 2.0 bulk insertmanyvalues.

Runs both strategies against a fresh in-memory SQLite at N = 1k and 10k.
Reproducible: same seed, identical rows fed to each strategy."""

from __future__ import annotations

import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from salary import models  # noqa: F401 — register tables
from salary.db import Base
from salary.models.employee import Employee
from salary.seed import bulk_insert, generate_employee_rows


def _fresh_session():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)()


def _time(label: str, fn) -> float:
    t0 = time.perf_counter()
    fn()
    elapsed = time.perf_counter() - t0
    print(f"  {label:38s} {elapsed:6.3f}s")
    return elapsed


def bench_at(n: int) -> None:
    print(f"\nN = {n:,}")
    rows = generate_employee_rows(count=n, seed=42)

    # Strategy A: ORM add per row
    session = _fresh_session()

    def naive():
        for row in rows:
            session.add(Employee(**row))
        session.commit()

    t_naive = _time("naive: ORM add per row", naive)
    session.close()

    # Strategy B: single insertmanyvalues
    session = _fresh_session()

    def bulk():
        bulk_insert(session, rows)
        session.commit()

    t_bulk = _time("bulk: insertmanyvalues", bulk)
    session.close()

    print(f"  speedup: {t_naive / t_bulk:.1f}x")


def main() -> None:
    for n in (1_000, 10_000):
        bench_at(n)


if __name__ == "__main__":
    main()
