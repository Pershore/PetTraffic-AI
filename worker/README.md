# PetTraffic central API – Phase 3

## What this adds

This is an isolated Cloudflare Worker + D1 control API scaffold. It does not change the Cloudflare Pages site, DNS, or the existing GitHub Actions schedules.

The API provides:
- `GET /health` – verifies the Worker can query D1 and returns the latest 15-minute site/D1 heartbeat (or `heartbeat: null` before the first scheduled check).
- `POST /v1/events` – stores allow-listed aggregate snapshots.
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

GitHub's `automation-history` branch remains the source of truth; D1 is an additional aggregate event store, not a replacement. The first post-deployment scheduled snapshot sync is still required to verify live OIDC-authenticated event write/read. Task enqueue/claim/complete remain deliberately disabled until a separate agent identity is implemented and tested. No workflow currently switches history storage from GitHub to D1.

## Local tests

From this directory run:

```sh
npm test
```

The GitHub PR workflow runs these tests. The deploy workflow runs only when manually dispatched.
