# AI Usage Log

The brief asks for *"intentional AI use while maintaining correctness and
quality."* This is the honest record of how AI tools were used in this
assessment — including the moments where the AI was wrong, the moments
where I rejected its suggestions, and the patterns that emerged over the
session.

## TL;DR

I used Claude Code (Opus 4.7) in the terminal as a pair programmer / executor:

- **I** set goals, constraints (Python/FastAPI, AWS, lowest cost), verified
  each phase before approving the next, and pushed back when the AI
  over-engineered.
- **Claude** wrote the code, ran the test suite, generated the docs,
  surfaced trade-offs, and — importantly — self-critiqued in dedicated
  review passes.

The output is what we built together, not what Claude produced alone.
Every architectural choice was explicitly approved or rejected before it
landed on disk. Every phase ended with a verification step (curl, pytest,
or Playwright) before the next phase started.

## The split

| I did | Claude did |
|---|---|
| Pick the stack (Python/FastAPI + SQLite + Next.js) | Wrote all the code, all the tests, all the commit messages |
| Set the cost ceiling ($0 free tier, no Postgres) | Researched current state (App Runner deprecated, SQLAlchemy 2.0 changes) |
| Demand verification after every phase | Ran the test suite, captured output, reported honestly |
| Push back when proposals were too complex | Generated DESIGN.md / PERFORMANCE.md / this doc |
| Set workflow preferences (venv, mobile-first audit) | Self-reviewed when asked, caught its own mistakes |
| Approve or reject each commit | Wrote the migration files, the seed script, the UI components |

This is not "AI did everything." It's "AI implemented a plan I directed,
and I verified at each stage."

## Patterns built up over the session

- **TDD with paired commits.** Every test was a RED commit, every
  implementation a GREEN commit, often followed by REFACTOR. Phase 1
  shows ~10 consecutive R/G/R cycles for the domain + repository layer.
  The commit log reads like a TDD workshop transcript.

- **Per-phase verification.** End of each phase, the AI produced a report:
  commit count, test count, what's done, what's deferred. I'd
  occasionally ask for a smoke test (curl, Playwright) before approving
  the next phase. This caught real bugs — see "mobile-first claim" below.

- **Honest deferral, documented.** When something was valuable but out of
  scope (frontend Vitest, manager hierarchy, soft delete, multi-currency
  normalisation), we said so explicitly in DESIGN.md rather than pretend
  the gap didn't exist.

- **Conventional commit prefixes** (`test(...)`, `feat(...)`, `chore(...)`,
  `refactor(...)`, `perf(...)`) with RED/GREEN markers in the subject
  line. The log is readable as a story.

## Where I pushed back on AI suggestions

These are the moments where I steered the AI away from its default
recommendation.

### Lambda vs Fargate vs EC2

Claude's first AWS recommendation was a textbook ECS Fargate + ALB + RDS
stack — *"production AWS, ~$30-40/mo."* I asked *"what would smallest ECS
cost?"* and the answer involved compromises (Fargate Spot, no ALB, EFS for
SQLite) that ended up *more complex* than EC2 + Docker Compose at a
similar price. We landed on EC2 t3.micro + SQLite + Caddy — $0 on free
tier, ~$3/mo after. The defensible interview answer: *"for this workload,
the simplest deploy that meets requirements is the right one."*

### Python on Lambda vs Python in a container

I asked *"can we deploy Python 3.12 as Lambda, but do they even need
different — can we just build everything on Next.js?"*. That single
question forced an honest three-way comparison (Next.js full-stack vs
FastAPI on Lambda vs FastAPI on Fargate) rather than the AI defaulting
to the polyglot architecture. We kept Python (the JD signal matters) but
only after weighing the alternative.

### Service layer for plain CRUD

Claude's initial routing plan included a service layer for every CRUD
endpoint. I implicitly accepted; on the next pass Claude reconsidered
and skipped it as YAGNI — explained in DESIGN.md. The service layer
finally arrived in Phase 3 when insights actually needed shared rules
(active-only filter). This is the difference between architectural
discipline and ceremony.

## Where AI got things wrong (and we caught them)

These matter most. AI-assisted work is only honest if you show where
the AI was wrong.

### The smushed RED+GREEN commit (Phase 1)

Claude committed something labelled `test(repo): RED — ...` that actually
contained both new failing tests *and* the production code for older
passing tests. Caught it before moving on. Used `git reset HEAD~1`,
re-split into a proper `feat(repo): GREEN — create + get_by_id` commit
followed by the clean `test(repo): RED — list/update/delete` commit.
The recovery itself is visible in the log:
`fd330b8 → ec1f3d0 → 01a201f → 3885fce`. Catching commit-vs-message
drift in real time is part of TDD discipline.

### Percentile test math wrong (Phase 3)

I asked for tests on `statistics.quantiles([100,200,300,400])`. Claude
asserted `p25=150, p50=250, p75=350, p90=380`. The test ran red with
actual values `[125, 250, 375]` — and `p90 = 450`, *higher than the max*.
The default `method='exclusive'` extrapolates beyond the data range.
Switched to `method='inclusive'` (matches numpy/pandas), which is
bounded. Updated test expectations to the correct values:
`p25=175, p50=250, p75=325, p90=370`. The GREEN commit message documents
the choice. This is exactly why we write tests *first*: claims get
checked against reality.

### The optimistic bulk-insert claim (Phase 4)

DESIGN.md predicted SQLAlchemy bulk insert would be *"~15× faster than
the ORM default"* — a common quoted benchmark. Actual measurement on
Python 3.14 + SQLAlchemy 2.0: **4× faster**. SQLAlchemy 2.0 made the ORM
path use `insertmanyvalues` automatically, narrowing the gap. Updated
PERFORMANCE.md honestly rather than retroactively rewriting DESIGN.md.

### The mobile-first claim that wasn't (Phase 5)

After Phase 5, Claude reported the frontend was complete and "mobile-first"
(because grid-cols-1 default → md:grid-cols-2 etc). I asked
*"verify frontend is mobile first and good enough ultrathink."* Resized
Playwright to 375×812 and found: **the employees list page was hiding
5 of 7 columns with `overflow-hidden`** — users on mobile couldn't see
salary or status at all. Worst page of the app, worst possible bug.
Fixed with progressive column visibility (`hidden md:table-cell`
patterns) and inline mobile context (employee_id + email + role/country
folded under the Name cell on small screens).

Lesson: *"looks responsive in code"* ≠ *"is responsive in reality."*
Should have done the viewport audit before claiming the phase was done.

### Next.js 16 dev cross-origin block (Phase 5 verification)

Navigated Playwright to `http://127.0.0.1:3001` — page returned 200 HTML
but never hydrated React. Zero fetches to the backend in the network log.
Diagnosis: Next.js 16's `allowedDevOrigins` blocks 127.0.0.1 from loading
dev resources when the server is bound on `localhost`. Switched to
`http://localhost:3001` → fixed instantly. In production this won't
matter (single origin behind a real domain), but worth flagging in
deploy docs.

### Missing CORS middleware (Phase 5 verification)

When the frontend first tried to call the backend, CORS preflight
failed because I'd never added the middleware. Fixed in a 17-line commit
that reads CORS_ORIGINS from env so prod doesn't need a rebuild for new
origins.

### Node OOM during `next build` on t4g.nano (Phase 6 deploy)

EC2 build crashed with:

> FATAL ERROR: Ineffective mark-compacts near heap limit
> Allocation failed - JavaScript heap out of memory
> Next.js build worker exited with code: null and signal: SIGABRT

t4g.nano is 408 MB RAM + 1 GB swap. V8's default
`--max-old-space-size` is 4 GB, so Node tried to grow into swap, the
working set didn't fit, the kernel OOM-killer fired. Fixed by capping
the heap (`NODE_OPTIONS=--max-old-space-size=768`) so V8 GCs early
*and* bumping the swapfile from 1 GB to 2 GB so the bounded heap plus
node_modules plus the Next.js compiler all fit. Build went from
crash-at-22-min to clean-at-5-min.

### Caddy serving stale Caddyfile after `git pull` (Phase 6 deploy)

After `git pull` brought in the new Caddyfile (split `/api/*` →
FastAPI, `/*` → Next.js), Caddy's `exec caddy reload` reported success
but kept proxying everything to FastAPI. Diagnosis: `git pull` replaces
files atomically (write new file → rename over old), which **orphans the
inode the docker bind mount was pointing at**. Caddy was still reading
the deleted file via its old fd. Fix: `docker compose up -d
--force-recreate caddy` to re-resolve the bind mount path. Now baked
into the redeploy snippet in DEPLOY.md.

## Where AI caught things I would have missed

- **App Runner being in maintenance mode.** I picked App Runner as the
  obvious AWS choice (it's the simplest). Web research turned up: no new
  customers after April 2026. ECS Express Mode is the recommended path
  now. Pivoted before writing any infra code.

- **SQLAlchemy 2.0's `MappedAsDataclass` for construction-time defaults.**
  When the first test wanted `status` to default to `"active"` at object
  construction time, SQLAlchemy's `mapped_column(default=...)` doesn't
  trigger until INSERT. The clean 2.0-idiomatic fix is `MappedAsDataclass`
  — surfaced before I'd have hand-rolled an `__init__` override.

- **CheckConstraint for negative salaries.** Caught in the Phase 1
  self-review: the seed script bulk-inserts past Pydantic validation,
  so the DB itself needs to enforce. Added the constraint + Alembic
  migration (`169503585ddb`).

- **`(country, currency_code)` aggregation grouping.** It's tempting to
  `GROUP BY country` for the insights, but an MNC paying expats in USD
  inside India would silently corrupt the average. Surfaced this in
  DESIGN.md §5 and built the schema accordingly.

## Key user prompts that shaped the work

Paraphrased / verbatim where possible. These shifted direction:

- *"lets plan it properly again verify plan is right research internet if
  needed, we will deploy on aws"* — triggered the architecture research
  that found App Runner deprecated.
- *"i want the lesses cost and what should i do we will use python fast
  api"* — locked in the cheap EC2+SQLite path.
- *"use venv for python"* — saved to AI memory for future sessions in
  this directory.
- *"verify after every phase"* — set the cadence rhythm.
- *"we can deploy python3.12 as lambda but do they even need different we
  can build on next js everything"* — forced an honest comparison rather
  than letting me default to polyglot.
- *"what would smallest ecs cost"* — produced the cost table that
  ultimately killed the ECS proposal.
- *"verify frontend is mobile first and good enough ultrathink"* — caught
  the broken mobile list page.
- The literal `ultrathink` token on several turns — explicit signal to
  reason more deeply than the default brevity preference.

## What I'd do differently next time

- **Mobile audit during, not after.** The broken list page would have
  been caught in Phase 5 if I'd resized the viewport during initial
  verification, not after sign-off.
- **Benchmark before predicting.** The 15× speedup claim in DESIGN.md was
  wrong because I quoted a common figure without measuring. Numbers in
  docs should be cited or measured, not both implied.
- **Make tests fail for the *right* reason.** Several RED tests passed
  incidentally — a 404 on a route that doesn't exist yet looks the same
  as a 404 we'll later return on purpose. Acceptable but weaker than a
  test that fails because the behaviour is genuinely missing.
- **CORS up-front.** Should have added the middleware when we planned a
  cross-origin frontend, not waited for the browser smoke test to fail.
- **Write this doc incrementally.** AI_USAGE.md should have grown phase
  by phase, not been retrofitted at the end. The content is honest but
  some specifics had to be reconstructed from the git log.

## Tools used

- **Claude Code (Opus 4.7)** in the terminal, with Read / Edit / Write /
  Bash / TaskCreate / web search.
- **Playwright MCP** for visual + interaction verification of the
  frontend (3 real browser screenshots, full CRUD walkthrough).
- **AI Memory**: persistent feedback like *"always use per-project .venv
  for Python in this directory"* saved across sessions.
- **Web search**: verified current state of App Runner (maintenance mode),
  SQLAlchemy 2.0 bulk insert behaviour, Next.js 16 dev origins, US Census
  public-domain name files.

## What this doc is not

- A complete transcript. The actual conversation was thousands of lines;
  this is the curated, intent-revealing parts.
- A confession that the AI did everything. It didn't. It executed; I
  directed, verified, and pushed back.
- A claim that nothing was missed. The honest gaps live in the
  verification report — frontend Vitest tests, the Phase 6 deploy and
  video demo, the TRADE_OFFS.md / ARCHITECTURE.md extractions from
  DESIGN.md.

The product is what it is: a working, tested, mobile-responsive HR tool
built with deliberate AI assistance, honestly documented.
