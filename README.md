# Salary Management

A small, end-to-end salary management tool for an HR Manager of a 10,000-person org.
Built as the [Incubyte Software Craftsperson assessment](https://blog.incubyte.co/blog/tdd-assessment/).

## Live

| | URL |
|---|---|
| **App via CloudFront** (recommended) | https://d334cun2ulu6ii.cloudfront.net |
| **App direct from EC2** | https://13-202-206-123.sslip.io |
| **Demo video** (40 s, silent, 1920×1080) | [`docs/demo.mp4`](docs/demo.mp4) |

Same app behind both URLs — Caddy on EC2 serves the Next.js frontend
and proxies `/api/*` to FastAPI; CloudFront sits in front for edge TLS
and static-chunk caching.

OpenAPI docs: [`/api/docs`](https://d334cun2ulu6ii.cloudfront.net/api/docs).

## What's where

```
backend/   FastAPI + SQLAlchemy 2.0 + Alembic + SQLite
           62 pytest tests, 0.45 s, factory + in-memory DB
frontend/  Next.js 16 App Router + shadcn/ui + TanStack Query
           Mobile-first responsive (verified at 375 px and 1400 px)
infra/     OpenTofu — EC2 t4g.nano + EIP + SG + S3 backups + CloudFront
docs/      The artifacts the brief asks for, see index below
```

## Docs index

- [`docs/DESIGN.md`](docs/DESIGN.md) — schema rationale, insight choices, currency stance, architecture, trade-offs, out-of-scope (written *before* code)
- [`docs/PERFORMANCE.md`](docs/PERFORMANCE.md) — seed-script benchmark (10K in 0.08 s, 4× ORM speedup), insight-query budgets, what would change at higher scale
- [`docs/DEPLOY.md`](docs/DEPLOY.md) — runbook (provision, ssh, seed, debug, teardown), CloudFront chapter, cost breakdown
- [`docs/AI_USAGE.md`](docs/AI_USAGE.md) — honest record of how Claude was used, what it got wrong, what I caught, what I rejected
- [`docs/VIDEO_SCRIPT.md`](docs/VIDEO_SCRIPT.md) — what the demo recording covers

## Quick start (local dev)

### Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
python -m salary.seed --count 10000
uvicorn salary.main:app --reload --port 8765
pytest                                # 62 tests, ~0.5 s
```

### Frontend
```bash
cd frontend
npm install
# Same-origin via Caddy in prod; for local dev point at the local backend:
NEXT_PUBLIC_API_URL=http://localhost:8765 npm run dev
# → http://localhost:3000
```

## Deploy (one command)

```bash
cd infra
tofu init && tofu apply       # ~5 min for AWS + ~5 min for cloud-init
tofu output cloudfront_url    # → https://dXXXX.cloudfront.net
```

See [`docs/DEPLOY.md`](docs/DEPLOY.md) for what gets provisioned, how
to SSH in, how to seed the deployed DB, and how to tear it all down.

## Commit history is the work

The git log is structured as RED → GREEN → REFACTOR cycles end-to-end:

```bash
git log --oneline | head -30
```

Most domain commits come in pairs:

```
test(employee): RED — salary is Decimal, not float
feat(employee): GREEN — salary (Numeric 12,2) and currency_code (ISO 4217)
```

A real TDD-discipline catch is documented in `docs/AI_USAGE.md`: one
RED commit accidentally included GREEN code, caught and re-split with
`git reset HEAD~1` into proper pairs (commits `fd330b8` → `ec1f3d0` →
`01a201f` → `3885fce`).

## Tech stack

| Layer | Choice | Why (full reasoning in DESIGN.md) |
|---|---|---|
| Backend | Python 3.12 + FastAPI | JD signal; typed; auto OpenAPI doc is a free artifact |
| ORM | SQLAlchemy 2.0 + Alembic | `insertmanyvalues` for fast seeds; real migrations |
| DB | SQLite (dev + prod) | Brief endorses it; HR-manager workload doesn't need Postgres yet |
| Frontend | Next.js 16 App Router + TypeScript strict | Brief allows React/Next; App Router is current |
| UI | shadcn/ui + Tailwind | Lets you show taste, not pick from a fixed palette |
| Data | TanStack Query + relative `/api` URLs | Server pagination for 10K rows; same-origin → no CORS |
| Charts | Recharts | Lightweight for our handful of charts |
| Infra | OpenTofu (not Terraform — forward-looking 2026 choice) | State-managed, `tofu destroy` is the tear-down |
| Deploy | EC2 t4g.nano + Docker Compose + Caddy + sslip.io + CloudFront | $0 free-tier path; HTTPS with no domain via sslip.io; CloudFront for edge TLS |

## License

US Census name lists in `backend/src/salary/seed_data/` are
[public domain](backend/src/salary/seed_data/README.md). Everything
else: ask if you need to reuse it.
