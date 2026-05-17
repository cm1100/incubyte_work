# Video Demo Script

A 31-second silent walkthrough is committed at [`docs/demo.mp4`](demo.mp4).
It's a slideshow of Playwright screenshots taken against the live
CloudFront URL, stitched with `ffmpeg`. Five frames covering: employee
list (10 K rows), search ("james" → 5 matches), insights summary
(10 country rows), country drill-down (percentiles + per-job-title),
headcount charts.

The longer narrated script below is for an optional Loom recording —
~4–5 minutes, includes the architecture/TDD/AI-usage walkthrough that
the silent demo can't convey.

Use the **live CloudFront URL** throughout so the reviewer sees the
actual deployed app:

`https://d334cun2ulu6ii.cloudfront.net`

The order below mirrors the cognitive flow a reviewer would want:
"is it working" → "how is it built" → "what's interesting about it".

## 0. Setup (off-camera)

- Two browser tabs:
  1. `https://d334cun2ulu6ii.cloudfront.net/employees`
  2. `https://github.com/cm1100/incubyte_work`
- IDE open on the project (any one of `salary/seed.py`,
  `repositories/employee.py`, or `services/insights_service.py`
  shows the layering)
- Terminal open in the repo root

## 1. The live app (~90 s)

1. Open `https://d334cun2ulu6ii.cloudfront.net` — note the redirect
   to `/employees`.
2. Show the paginated list: **"10,000 employees, server-paginated 25
   at a time, currency formatted per row's own locale."**
3. Search for `james` — point out the 5 matches across 10K rows
   returns instantly because the API is doing the work, not the
   browser.
4. Click into a row → detail page → show **Save** and **Delete** are
   real (don't actually delete unless you re-seed after).
5. Navigate to `/insights` — walk through:
   - "Salary by country" table (10 currencies, all formatted natively)
   - The country drill-down (switch from default `AU` to `IN`,
     percentiles + per-job-title table refresh)
   - The three headcount charts (active employees only, hence
     "9,528 of 10,000")

## 2. The architecture (~60 s)

Open `docs/DESIGN.md` and scroll to §7 (architecture diagram):

> "One EC2 t4g.nano in Mumbai, $3/mo. Docker Compose runs three
> containers — Caddy, FastAPI, Next.js. Caddy fronts both on a single
> sslip.io hostname with free Let's Encrypt TLS. CloudFront sits in
> front for global edge caching and TLS termination."

Open `infra/main.tf` briefly:

> "Provisioned with OpenTofu — chose it over Terraform for the open-
> source governance after HashiCorp's BUSL move. `tofu destroy` is the
> tear-down."

## 3. The TDD discipline (~60 s)

Terminal:

```bash
git log --oneline | head -30
```

Point out:

- The RED/GREEN/REFACTOR pattern in the subject lines
- One TDD-log mistake I caught and fixed in real-time:
  `fd330b8 → ec1f3d0 → 01a201f → 3885fce` (smushed RED+GREEN reset
  and re-split — documented in `docs/AI_USAGE.md`)

```bash
cd backend && .venv/bin/pytest --tb=no -q
```

→ `62 passed in 0.45s`. Mention: "all integration, sub-second, in-memory
SQLite."

## 4. The honest AI usage log (~30 s)

Open `docs/AI_USAGE.md`. Scroll to "Where things went wrong (and were
caught)":

> "Seven concrete bugs the AI got wrong, all caught — the percentile
> math, the mobile-first claim that broke the list page, the Node OOM,
> the Caddy inode race. The doc shows the workflow, not just the output."

## 5. Wrap (~15 s)

> "Repo: github.com/cm1100/incubyte_work — public, 65+ commits,
> commit log reads like a TDD workshop transcript. Live URLs in the
> README. `tofu destroy` cleans up for $0."

## Things deliberately NOT in the demo

- Authentication (not asked for; documented out-of-scope in DESIGN.md)
- Manager hierarchy / soft delete (same)
- Cross-currency salary normalisation (DESIGN.md §5 explains why)
- Frontend Vitest tests (deferred with reasoning in AI_USAGE.md)

If asked about any of them in the interview, the design doc has the
answer ready.
