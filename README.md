# Salary Management

A minimal yet usable salary management tool for an HR Manager. Manage 10,000+ employees, view salary insights, deployed end-to-end on AWS.

## Layout

```
backend/    FastAPI + SQLAlchemy + SQLite
frontend/   Next.js + shadcn/ui + TanStack Query
infra/      AWS CDK (Python) — EC2 + Amplify
docs/       Design notes, architecture, AI usage log, trade-offs
```

## Quick start

See `backend/README.md` and `frontend/README.md` once those scaffolds land.

## Design notes

See [`docs/DESIGN.md`](./docs/DESIGN.md) for schema rationale, insight choices, architecture, and trade-offs.
