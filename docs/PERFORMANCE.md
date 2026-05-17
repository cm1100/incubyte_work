# Performance Notes

## Seed script (10,000 employees)

The brief calls this out explicitly: *"Assume that engineers run this script regularly, and performance of the script matters."* So the seed script was built two ways and timed.

### Setup

- Apple M-series, Python 3.14.3, SQLAlchemy 2.0
- Fresh in-memory SQLite (no I/O contention) for the comparison
- Fresh on-disk SQLite for the end-to-end CLI run
- Deterministic generator (`random.Random(seed=42)`) so both strategies receive identical rows

### Results

| N | Strategy | Time | Notes |
|---|---|---|---|
| 1,000 | naive: `session.add(Employee(**row))` per row | **0.030 s** | ORM session tracks every object |
| 1,000 | bulk: `session.execute(insert(Employee), rows)` | **0.008 s** | one INSERT…VALUES via `insertmanyvalues` |
| 1,000 | speedup | **3.7×** | |
| 10,000 | naive | **0.255 s** | |
| 10,000 | bulk | **0.064 s** | |
| 10,000 | speedup | **4.0×** | |

End-to-end CLI (`python -m salary.seed --count 10000 --reset`) on a file-backed SQLite: **0.078 s** insert time, ~0.44 s wall-clock including Python startup, name-file load, and SQLAlchemy import.

### Why the gap is "only" ~4×, not the often-quoted 15×

SQLAlchemy 2.0's ORM `add()` has gotten significantly faster — `insertmanyvalues` is the default INSERT path for ORM operations too now, so naive ORM-per-object isn't as expensive as it used to be in 1.x. The big remaining cost is the per-object identity-map / autoflush bookkeeping. At 10K rows it costs us ~0.19 s; at 1M rows the gap widens nonlinearly.

### What the script does (and doesn't do)

**Does**
- Deterministic generation (fixed-seed `Random` → reproducible rows)
- Single transaction wrapping the entire insert
- `insert(Employee), rows` so SQLAlchemy uses `insertmanyvalues` automatically
- `--reset` flag wipes the table first when an engineer wants a clean baseline

**Doesn't (deliberately)**
- Drop indexes before insert and rebuild after — at 10K it's not necessary; would matter at 1M+
- COPY-style ingest — Postgres-specific, not portable to the SQLite dev path
- Parallel inserts — SQLite is a single-writer, so no win there

## Insight query performance

The query patterns:

- `GET /insights/by-country` → `GROUP BY country, currency_code` (full-table aggregate)
- `GET /insights/by-country/{c}/by-job-title` → `WHERE country=? GROUP BY job_title, currency_code` — composite `(country, job_title)` index handles both clauses
- `GET /insights/by-country/{c}/percentiles` → `WHERE country=? ORDER BY currency_code, salary` — uses the `country` index
- `GET /insights/headcount` → 3× `GROUP BY` queries

At 10K rows on SQLite, all four return well under 50 ms with no special tuning. Real-world bottleneck before 1M rows would be the Python-side serialization of large response payloads, not the SQL.

## What I'd change at higher scale (not implemented)

- **100K rows**: nothing changes — index strategy still holds, payloads stay small via server-side pagination.
- **1M+ rows**: switch to Postgres, add materialized views for the insight rollups (refresh nightly), drop the per-row currency_code from the response in favour of denormalised currency-aware tables.
- **10M+ rows**: re-evaluate whether SQLite-via-Alembic is still the right baseline; consider ClickHouse or BigQuery for the insight side and keep Postgres just for CRUD.
