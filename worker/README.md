# PetTraffic central API – Phase 3

## What this adds

This is an isolated Cloudflare Worker + D1 control API scaffold. It does not change the Cloudflare Pages site, DNS, or the existing GitHub Actions schedules.

The API provides:
- `GET /health` – verifies the Worker can query D1 and returns the latest 15-minute site/D1 heartbeat (or `heartbeat: null` before the first scheduled check).
- `POST /v1/events` – stores allow-listed aggregate snapshots and deduplicates repeated submissions by event kind and source workflow run ID.
- `GET /v1/events` – reads the latest 100 aggregate events (optionally filtered by kind).
- `POST /v1/tasks`, `POST /v1/tasks/claim`, and `POST /v1/tasks/{id}/complete` – bounded task-queue routes. In the secure task-runner rollout they remain disabled by default (`503 task_api_not_enabled`) until the Worker runtime flag is deliberately enabled.

Specialist names: `coordinator`, `analytics`, `topics`, `technical-seo`, `content-review`.

Task types are deliberately read-only. There is no article publishing, website editing, DNS editing, or arbitrary command execution endpoint.

## Privacy and security

- All `/v1/*` routes require a short-lived GitHub Actions OIDC JWT.
- The Worker verifies the JWT signature against GitHub's published JWKS and validates issuer, audience, expiry, repository name and immutable owner/repository IDs, main-branch ref, exact workflow path, and `workflow_run` event. This repository was created after GitHub's 2026-07-15 immutable-subject rollout, so the expected `sub` includes owner and repository IDs.
- The snapshot-sync identity is restricted to `/v1/events`. Task creation and task execution use separate exact workflow OIDC identities and separate endpoint roles.
- No long-lived PetTraffic API bearer token or `API_TOKEN` Worker secret is required.
- `id-token: write` is scoped to the snapshot-sync workflow, the owner-command dispatcher job, and the gated read-only task-runner job; pull-request test jobs do not receive it.
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

## Secure read-only task runner

The first task runner is deliberately narrow and event-driven:

- Three exact OIDC identities are separated: `sync-control-api.yml` writes aggregate events; the owner-only `dispatch-daily-suite.yml` workflow enqueues one fixed task; `run-readonly-tasks.yml` claims, executes and completes that task.
- All identities require a short-lived GitHub OIDC JWT with the exact issuer, audience, immutable repository/owner IDs, main ref, workflow path, event type and valid signature.
- The only enabled task type is `check_site` for `technical-seo`, with the exact payload `{ "target": "public_site" }`. The runner maps it to the fixed `agent/check_live_site.py` script; task data is never interpreted as a shell command.
- The only enqueue command is `/pettraffic-enqueue-site-check` on issue #145. The bridge accepts it only as an exact comment from repository owner `Pershore`; the bridge then dispatches one GitHub-hosted runner workflow.
- The runner executes one task per run, with a 600-second script timeout, a 30-minute claim lease and at most three attempts. It requests a fresh OIDC token to complete the task, then reads the stored result back from D1 and verifies the status and exit code.
- Worker task routes are enabled in `wrangler.toml`, but every route still fails closed without the matching OIDC role. The public `/control/` dashboard remains read-only; no browser bearer token or public write route is added.
- The worker role does not permit content publishing, live-site editing, DNS changes, Cloudflare settings, spending, arbitrary commands or ARO Vet changes.

This proves a bounded cloud task lifecycle only after the post-merge Worker deployment and a real owner-command test complete enqueue → claim → fixed execution → complete → D1 readback. It does not make the public dashboard an authenticated one-click interface; private dashboard access remains a separate project.

## Local tests

From this directory run:

```sh
npm test
```

The GitHub PR workflow runs these tests. The deploy workflow runs only when manually dispatched.


## Free-plan AI agent orchestration (merged; initial live run verified; post-sync schedule update pending)

The internal daily orchestrator uses Cloudflare Workers AI and D1. Its primary target is 13:20 Europe/Vilnius year-round: cron triggers at 10:20 and 11:20 UTC, with an IANA timezone gate for the one matching local time. Before reserving the daily run, the Worker checks that at least one analytics or topic snapshot from the current Vilnius day has reached D1. A snapshot is eligible only when its provenance is either a true Daily-suite `event=schedule` or a separately verified owner-only fallback: the exact `/pettraffic-run-daily-suite` comment on issue #145, posted by repository owner `Pershore`, linked to the successful owner-command bridge run and the resulting Daily-suite `workflow_dispatch`. Plain manual dispatches, pushes, PRs and other events remain ineligible. If the daily suite or D1 sync is delayed, later 15-minute heartbeat events after 13:20 repeat the readiness check and start the cycle once same-day data arrives. The unique `agent_runs.run_date` row keeps the cycle idempotent, so the catch-up path cannot run a second time that day.

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
