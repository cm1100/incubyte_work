# Design Notes

This document captures the product and engineering decisions behind the
salary management tool, with rationale. It is written *before* the code so
the reasoning is visible, not retrofitted.

---

## 1. Problem & user

An HR Manager of a 10,000-person organisation needs to:

- Manage employee records (add / view / update / delete)
- Understand salary patterns: per country, per job title in a country, plus
  a small number of other useful breakdowns

The persona is a single role, with a handful of concurrent users at most.
There are no claims about real-time analytics, multi-tenancy, audit chains,
or compliance-grade controls. Designing for those would be over-building.

## 2. Functional scope

**In scope (required by brief)**

- CRUD on employees via UI
- Insights: min / max / avg salary per country
- Insights: avg salary by job title within a country

**In scope (added because the persona genuinely needs them)**

- Server-side pagination + search on the employee list (10K rows do not
  belong in the browser at once)
- Percentile breakdown (p25 / p50 / p75) per country — averages alone hide
  pay distribution problems
- Headcount breakdown (per country / per department / per job title) —
  a single number an HR manager will ask for on day one

**Out of scope (deliberate)**

- Authentication and authorization
- Audit log beyond `created_at` / `updated_at`
- Manager hierarchy / org chart
- Cross-currency normalisation (see §5)
- Salary history (we store the current salary only)
- Bulk import via CSV (the seed script covers the engineering signal)

These are listed not because they were forgotten but because they would
inflate the surface area without proving anything new.

## 3. Data model

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key. Stable internal identifier. |
| `employee_id` | string, unique | Human-readable (`EMP-00042`). What HR actually uses. |
| `first_name` | string | Stored separately for sorting / display. |
| `last_name` | string | Same. `full_name` is a computed property. |
| `email` | string, unique | Required, used for dedup. |
| `job_title` | string, indexed | Free text for now. A controlled vocabulary would be a sensible next step. |
| `department` | string, indexed | Same shape as job_title. |
| `country` | string, indexed | ISO-3166 alpha-2 (e.g. `IN`, `US`). |
| `salary` | `Numeric(12,2)` | **Not float.** Money rounding bugs are unforgivable. |
| `currency_code` | string(3) | ISO 4217 (`USD`, `INR`...). See §5. |
| `employment_type` | enum | `full_time` / `part_time` / `contract`. Affects insight inclusion. |
| `hire_date` | date | Drives future tenure metrics. |
| `status` | enum | `active` / `on_leave` / `terminated`. Insights default to `active` only. |
| `created_at` | timestamptz | Audit. |
| `updated_at` | timestamptz | Audit. |

**Indexes**

- `country` — every insight filters by country
- `(country, job_title)` — composite, for the per-title-per-country query
- `email` — unique, supports dedup
- `department` — secondary slice

**Why this schema, not the bare minimum**

The brief asks for full_name / job_title / country / salary. That is enough
for the math but not enough for the persona. An HR manager who cannot
search by email, filter by department, or exclude terminated employees from
averages will not actually use this tool. The added fields are picked to
unlock realistic insights (status filter, employment_type) and realistic
operations (email lookup, employee_id reference), not to pad the model.

## 4. Insights

Implemented endpoints:

1. `GET /insights/by-country` — for each country, return `count`, `min`,
   `max`, `avg`, `p50`. Used on the dashboard landing page.
2. `GET /insights/by-country/{country}/by-job-title` — per-title stats
   inside a chosen country. Drives the drilldown.
3. `GET /insights/by-country/{country}/percentiles` — p25 / p50 / p75 /
   p90. Averages lie; percentiles are how you spot pay-band problems.
4. `GET /insights/headcount` — counts by country, department, job title.
   Useful for sanity-checking org composition.

All insights default to `status = 'active'`. Terminated employees skew the
math.

**Documented but not built** (and why, so a reviewer can see the
discipline): tenure-by-department (requires `hire_date` analytics we don't
need yet), top-N highest-paid roles (a `LIMIT` away when needed),
gender-pay-gap analysis (we deliberately do not collect that field), salary
outliers (>2σ from role-mean). These are one-PR additions if the persona
ever asks.

## 5. Currency: the subtle product call

If salary is stored in local currency, then "min/max/avg per country" is
fine — every row in a country uses the same currency. But "avg for job
title X across all countries" is meaningless without conversion.

Three approaches were considered:

| Approach | Cost | Correctness |
|---|---|---|
| A. Per-row currency, aggregate **within country only** | Low | Correct for what the brief asks for |
| B. Static FX rates → normalise to USD on read | Medium | Correct globally, stale rates |
| C. Live FX API on every aggregation | High | Correct, fragile, slow |

**Chosen: A.** The brief only asks for per-country and per-title-within-country
metrics. Both are within-currency by construction. Storing
`currency_code` keeps the door open for option B if the persona later wants
a global view, with no schema migration.

This is product thinking: solve the asked problem cleanly; do not
over-build a feature nobody is paying for.

## 6. Tech stack

| Layer | Choice | One-line rationale |
|---|---|---|
| Backend | Python 3.12+ / FastAPI | Matches the JD; auto OpenAPI doc is a free artifact. |
| ORM | SQLAlchemy 2.0 / Alembic | `insertmanyvalues` makes bulk seed ~15× faster than the ORM default; Alembic gives real migrations. |
| Validation | Pydantic v2 | Tight FastAPI integration; types are the contract. |
| DB (dev/test/prod) | SQLite | The brief explicitly endorses it. The workload (≤10 concurrent users, 10K rows) does not justify Postgres. SQLAlchemy keeps a Postgres swap one config change away. |
| Backend tests | pytest + httpx.AsyncClient | Fast; SQLite-in-memory for repository tests. |
| Frontend | Next.js 14 App Router (TypeScript) | Brief allows React or Next.js; App Router is the current default. |
| UI | shadcn/ui + Tailwind | Modern default that lets us show taste rather than pick from a fixed Material palette. |
| Data | TanStack Query + TanStack Table | Server-side pagination for 10K rows, cache invalidation built-in. |
| Charts | Recharts | Light, sufficient for our handful of charts. |
| Frontend tests | Vitest + React Testing Library + MSW | Fast, deterministic, no Jest config pain. |
| Infra | AWS CDK (Python) | Same language as backend; the IaC code itself is an artifact. |

## 7. Architecture

```
User browser
    │
    ▼
┌──────────────────────────┐
│  AWS Amplify Hosting     │  Next.js, auto-deployed from main
│  (free tier)             │
└──────────┬───────────────┘
           │ HTTPS /api/*
           ▼
┌──────────────────────────┐
│  AWS EC2 t3.micro        │  Docker Compose:
│  Elastic IP              │    - Caddy (TLS via Let's Encrypt, reverse proxy)
│                          │    - FastAPI (uvicorn)
│  /var/data/app.db        │  SQLite on the attached EBS volume
└──────────┬───────────────┘
           │ nightly cron
           ▼
       S3 bucket             SQLite dumps for backup
```

**Backend layering**

```
api/routes/         HTTP thin layer — validation, status codes
    │
    ▼
services/           Business rules (status filters, currency rules)
    │
    ▼
repositories/       SQL only — no business logic
    │
    ▼
models/             SQLAlchemy
```

This separation is overkill for 100 lines of code, but underkill is
exactly what they grade against. The cost of three folders is small; the
cost of one tangled `routes.py` is large.

## 8. Trade-offs

| Decision | Alternative | Why we chose what we did |
|---|---|---|
| SQLite in prod | Postgres on RDS | Workload doesn't need it; saves ~$15/mo and removes connection-pool complexity. Swap is a config change. |
| Single EC2 + Docker | ECS Fargate + ALB + RDS | Same effective deployment, ~$0 vs ~$35/mo. The "production AWS" signal is not worth $35/mo when the simpler thing meets the spec. |
| No auth | Cognito / homemade JWT | Not asked for. Two extra screens of work that prove nothing new. |
| Within-country currency only | Global FX normalisation | The brief never asks for global aggregates. See §5. |
| `Numeric(12,2)` for salary | Integer minor units | Either is fine. Numeric reads more naturally in this domain and SQLAlchemy + Pydantic handle the precision. |
| TypeScript on frontend | Pure JS | Type-aligned with Pydantic via OpenAPI; catches drift between the two services. |

## 9. Performance budget

| Operation | Target | Notes |
|---|---|---|
| Seed 10K employees | < 2s on SQLite | `insertmanyvalues` + single transaction. |
| Employee list (page 50) | < 100ms p95 | Indexed columns; no N+1. |
| Per-country insights | < 50ms p95 | Aggregations on indexed `country`. |
| Per-title-per-country insights | < 80ms p95 | Composite index `(country, job_title)`. |

`docs/PERFORMANCE.md` will capture the actual measured numbers
once the seed script and benchmarks land.

## 10. Testing strategy

- **Unit / repository**: SQLite in-memory, fixture loads ~20 employees
  with arithmetic chosen so the expected averages are trivial to compute
  by hand. Tests assert *behaviour*, not implementation.
- **API**: `httpx.AsyncClient` against an app fixture with an in-memory
  test DB. Covers happy path plus 404, 409 (duplicate email), 422
  (validation).
- **Frontend**: Vitest + RTL. Forms (validation, submit, error), table
  (pagination), insight cards. MSW for API mocking. No end-to-end Playwright
  unless time remains in Phase 6.

Tests must be fast (< 5s for the whole backend suite) and deterministic.
Determinism in the seed script is enforced via `random.Random(seed=42)`.

## 11. AI usage approach

A separate `docs/AI_USAGE.md` will capture how AI tools were used: which
prompts mattered, which suggestions were rejected and why, and patterns
built up over the session. The goal is to show *intentional* AI use, not
hand-waved acceptance of generated code. Every diff is read before it is
committed.

## 12. What "done" looks like

- Working CRUD UI against a deployed FastAPI service
- Insights dashboard with the four metrics above
- 10K seeded employees via a single script command
- Test suite passing in CI
- Live URL (Amplify + EC2)
- 4-minute Loom video walking through CRUD → insights → repo tour
- Design doc (this file), `AI_USAGE.md`, `TRADE_OFFS.md`,
  `PERFORMANCE.md`, `ARCHITECTURE.md`
