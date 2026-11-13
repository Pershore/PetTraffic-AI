# PetTraffic central API – Phase 3

## What this adds

This is an isolated Cloudflare Worker + D1 control API scaffold. It does not change the Cloudflare Pages site, DNS, or the existing GitHub Actions schedules.

The API provides:
- `GET /health` – verifies the Worker can query D1 and returns the latest 15-minute site/D1 heartbeat (or `heartbeat: null` before the first scheduled check).
- `POST /v1/events` – stores allow-listed aggregate snapshots and deduplicates repeated submissions by event kind and source workflow run ID.
- `GET /v1/events` – reads the latest 100 aggregate events (optionally filtered by kind).
- `POST /v1/tasks`, `POST /v1/tasks/claim`, and `POST /v1/tasks/{id}/complete` – scaffolded for future agents; intentionally return `503 task_api_not_enabled` until a separate agent identity and authorization policy are implemented.

Specialist names: `coordinator`, `analytics`, `topics`, `technical-seo`, `content-review`.

Task types are deliberately read-only. There is no article publishing, website editing, DNS editing, or arbitrary command execution endpoint.

## Privacy and security

- All `/v1/*` routes require a short-lived GitHub Actions OIDC JWT.
- The Worker verifies the JWT signature against GitHub's published JWKS and validates issuer, audience, expiry, repository name and immutable owner/repository IDs, main-branch ref, exact workflow path, and `workflow_run` event. This repository was created after GitHub's 2026-07-15 immutable-subject rollout, so the expected `sub` includes owner and repository IDs.
- The current sync identity is restricted to `/v1/events`; task queue routes remain disabled until separate agent authentication is configured.
- No long-lived PetTraffic API bearer token or `API_TOKEN` Worker secret is required.
- Only the trusted sync job receives `id-token: write`; pull-request test jobs do not.
- Request bodies are size-limited; payloads reject keys resembling personal identifiers, search query text, credentials, or cookies.
- SQL values are parameterized.
- CORS is restricted to the PetTraffic Pages origin; server-to-server GitHub Actions calls do not need CORS.
- D1 stores aggregate snapshots and task metadata only. Do not send visitor-level analytics, raw Search Console queries, credentials, or health-related personal data.

## Cloudflare deployment status

As of 2026-11-12, the Cloudflare Worker `pettraffic-control-api` and D1 database `pettraffic-control` have been provisioned and deployed by GitHub Actions. Deployment run #30 completed successfully, including:
- Cloudflare API token, account, D1 database and Worker access validation.
- Application of D1 migrations.
- Worker deployment.
- Post-deployment `GET /health` check confirming D1 connectivity.
- Protected API smoke check confirming unauthenticated requests receive HTTP 401.

The Worker uses its default `.workers.dev` URL. No custom domain, DNS change, Pages change, or ARO Vet change is required.

For recovery or future Worker changes, use **GitHub Actions → Deploy PetTraffic control API → Run workflow**. Normal Worker code changes are deployed automatically after a tested pull request is merged into `main`.

## Cost and rollout

Check current Cloudflare plan limits and D1/Workers usage in the account before deployment. The scaffold itself is free to keep in GitHub; actual Cloudflare usage depends on plan limits and requests. No paid AI model is called.

## Automatic GitHub Actions sync

After the Worker is deployed, the `sync-control-api.yml` workflow requests a short-lived GitHub OIDC token at runtime and sends privacy-filtered aggregate snapshots. The Worker accepts only tokens issued to this repository's main-branch sync workflow. No `PETTRAFFIC_CONTROL_API_TOKEN` GitHub secret is needed. The optional `PETTRAFFIC_CONTROL_API_URL` variable may override the default Worker URL.

GitHub's `automation-history` branch remains the source of truth; D1 is an additional aggregate event store, not a replacement.

As of 2026-11-12, the live integration has been verified end-to-end:
- GitHub Actions OIDC authentication succeeds using the immutable owner/repository subject and IDs.
- Privacy-filtered analytics, control-center, and recommendation snapshots are accepted by the Worker.
- The sync workflow reads each newly written event back from D1 and fails if the event ID is not present.
- GitHub history remains the durable source of truth; no workflow has switched history storage to D1.

Task enqueue/claim/complete remain deliberately disabled until a separate agent identity and authorization policy are implemented and tested.

## Local tests

From this directory run:

```sh
npm test
```

The GitHub PR workflow runs these tests. The deploy workflow runs only when manually dispatched.


## Free-plan AI agent orchestration (merged; live run awaiting verification)

The internal daily orchestrator uses Cloudflare Workers AI and D1. It is configured for 10:20 Europe/Vilnius year-round: cron triggers at 07:20 and 08:20 UTC, and an IANA timezone gate allows exactly one invocation after the scheduled analytics/topic/health snapshots.

Five bounded inference calls are used per daily run: four read-only specialist reviews (analytics, topics, technical SEO, content review) and one coordinator synthesis. The report is stored in `agent_runs`. The run is idempotent per UTC day and has a hard application cap of five AI calls/day, with a maximum of 1024 generated tokens per call and bounded input text. Cloudflare Workers Free enforces its own daily Workers AI allocation; once exhausted, further requests fail instead of continuing on the Free plan.

The existing public `/v1/tasks*` routes remain disabled. Agent execution is internal to the scheduled Worker, so the analytics-only GitHub OIDC identity is not widened. All recommendations are advisory and require human approval. The content reviewer flags claims needing source verification; it does not certify veterinary facts. No paid API key, content publishing, site editing, DNS editing, or arbitrary command execution is enabled.

Model: `@cf/openai/gpt-oss-20b`. Recheck model availability and pricing before future model changes.


## Separate AI control core (merged to main)

The control core is a deterministic governance and memory layer separate from the specialist prompts:
- src/control-core.mjs converts coordinator output into a bounded decision and applies a fixed read-only policy. Model output cannot add permissions or actions.
- Migration 0003_control_core.sql stores the daily decision and a compact latest-state memory in D1. It stores aggregate project operational context only.
- The daily orchestrator persists the decision and compact memory after specialist synthesis. A persistence failure marks the orchestration run failed rather than reporting success.
- The core records recommendations and evidence gaps; it does not execute model-generated actions.
- Publication, live-site edits, DNS changes, ARO Vet changes, spending, Cloudflare permission changes and arbitrary code execution remain blocked. Production-impacting actions require separate explicit approval.
- Tests cover bounded decisions, malformed/model-supplied actions, D1 persistence and missing database handling.

The implementation and tests are merged to main. The PR test workflow passed, including the Worker Node.js and Python test suites. The deployment workflow supports both a push to main (for Worker code, migrations or Wrangler changes) and manual recovery. Post-merge deployment run #50 succeeded: D1 migrations were applied, the Worker was deployed, /health confirmed D1 plus control-core schema connectivity, and unauthenticated /v1/events returned HTTP 401. A fresh live check also confirmed control_core_schema=connected. As of 2026-11-14 00:31 Europe/Vilnius, the live `/health` endpoint reports the previous day's agent run as `2026-11-13 / failed / ai_calls=1`; today's 10:20 local agent cycle has not yet run. `control_core.status=not_started` and `memory_status=missing` are therefore pending verification, not evidence that today's cycle failed. The 15-minute heartbeat was confirmed at `2026-11-13T22:30:47.462Z` (00:30:47 local) with D1 connected. Do not report the control core as operational until a fresh successful run and memory persistence are confirmed.
