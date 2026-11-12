# PetTraffic central API – Phase 3

## What this adds

This is an isolated Cloudflare Worker + D1 control API scaffold. It does not change the Cloudflare Pages site, DNS, or the existing GitHub Actions schedules.

The API provides:
- `GET /health` – verifies the Worker can query D1.
- `POST /v1/events` – stores allow-listed aggregate snapshots.
- `GET /v1/events` – reads the latest 100 aggregate events (optionally filtered by kind).
- `POST /v1/tasks` – queues an allow-listed read-only task.
- `POST /v1/tasks/claim` – atomically claims the next task for a specialist.
- `POST /v1/tasks/{id}/complete` – records a task result for the claiming specialist.

Specialist names: `coordinator`, `analytics`, `topics`, `technical-seo`, `content-review`.

Task types are deliberately read-only. There is no article publishing, website editing, DNS editing, or arbitrary command execution endpoint.

## Privacy and security

- All `/v1/*` routes require a short-lived GitHub Actions OIDC JWT.
- The Worker verifies the JWT signature against GitHub's published JWKS and validates issuer, audience, expiry, repository, main-branch ref, exact workflow path, and `workflow_run` event.
- No long-lived PetTraffic API bearer token or `API_TOKEN` Worker secret is required.
- Only the trusted sync job receives `id-token: write`; pull-request test jobs do not.
- Request bodies are size-limited; payloads reject keys resembling personal identifiers, search query text, credentials, or cookies.
- SQL values are parameterized.
- CORS is restricted to the PetTraffic Pages origin; server-to-server GitHub Actions calls do not need CORS.
- D1 stores aggregate snapshots and task metadata only. Do not send visitor-level analytics, raw Search Console queries, credentials, or health-related personal data.

## One-time Cloudflare setup

Deployment is intentionally manual until the owner creates the D1 database and configures the least-privilege credentials.

1. In Cloudflare Dashboard, open **Storage & databases → D1 SQL Database** and create a database named `pettraffic-control`.
2. Copy its database ID.
3. Create an empty Worker named `pettraffic-control-api` in the Cloudflare Dashboard first. This allows deployment permissions to be scoped to that Worker instead of granting account-wide Worker creation rights.
4. Create a custom API token with **Workers Editor** for this Worker, **D1 Edit** for this database, and (only if Wrangler account discovery requires it) **Account Settings Read**. Do not grant Pages, DNS, Routes, or Global API Key access. Cloudflare documents Worker-scoped Editor access for deploying an existing Worker and D1 permissions for direct database operations. <https://developers.cloudflare.com/workers/authorization/> <https://developers.cloudflare.com/fundamentals/api/reference/permissions/>
5. In GitHub repository **Settings → Secrets and variables → Actions**, add:
   - Secret `CLOUDFLARE_API_TOKEN`
   - Variable `CLOUDFLARE_ACCOUNT_ID`
   - Variable `PETTRAFFIC_D1_DATABASE_ID`
6. Run **Actions → Deploy PetTraffic control API → Run workflow**. The workflow applies the D1 migration and deploys only this separate Worker.

The Worker has no production route/custom domain configured in this phase. It uses the default `.workers.dev` address if enabled for the account. Existing Pages deployment and DNS remain untouched. No separate Worker API token setup is needed; GitHub Actions authenticates with short-lived OIDC tokens.

## Cost and rollout

Check current Cloudflare plan limits and D1/Workers usage in the account before deployment. The scaffold itself is free to keep in GitHub; actual Cloudflare usage depends on plan limits and requests. No paid AI model is called.

## Automatic GitHub Actions sync

After the Worker is deployed, the `sync-control-api.yml` workflow requests a short-lived GitHub OIDC token at runtime and sends privacy-filtered aggregate snapshots. The Worker accepts only tokens issued to this repository's main-branch sync workflow. No `PETTRAFFIC_CONTROL_API_TOKEN` GitHub secret is needed. The optional `PETTRAFFIC_CONTROL_API_URL` variable may override the default Worker URL.

The existing GitHub history remains the source of truth during the first rollout. Do not switch existing workflows to D1 until:
1. the Worker health endpoint passes;
2. OIDC-authenticated event write/read checks pass;
3. task enqueue/claim/complete checks pass;
4. backup/export and recovery are tested.

## Local tests

From this directory run:

```sh
npm test
```

The GitHub PR workflow runs these tests. The deploy workflow runs only when manually dispatched.
