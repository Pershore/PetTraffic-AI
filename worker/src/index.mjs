import { runAgentOrchestration, isAgentScheduledEvent, isAgentCatchUpEvent, shouldRunAgentOrchestration } from "./agents.mjs";

const MAX_BODY_BYTES = 32 * 1024;
const ALLOWED_AGENTS = new Set(["coordinator", "analytics", "topics", "technical-seo", "content-review"]);
const ALLOWED_TASK_TYPES = new Set([
  "collect_analytics",
  "scan_topics",
  "check_site",
  "audit_technical_seo",
  "review_content_facts",
]);
const ALLOWED_EVENT_KINDS = new Set([
  "analytics_snapshot",
  "topic_snapshot",
  "control_center_snapshot",
  "recommendation_snapshot",
]);
const FORBIDDEN_KEY = /(^|_)(email|ip|ip_address|user_id|client_id|search_query|query_text|query|queries|token|secret|password|authorization|cookie)(_|$)/i;

function response(data, status = 200, origin = null) {
  const headers = {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    "x-content-type-options": "nosniff",
  };
  if (origin) {
    headers["access-control-allow-origin"] = origin;
    headers.vary = "Origin";
  }
  return new Response(JSON.stringify(data), { status, headers });
}

function summarizeEvidenceGapCategories(decision) {
  const categories = {
    model_output: 0,
    source_data: 0,
    source_unavailable: 0,
    insufficient_evidence: 0,
    other: 0,
  };
  for (const gap of Array.isArray(decision?.evidence_gaps) ? decision.evidence_gaps : []) {
    const value = typeof gap === "string" ? gap.toLowerCase() : "";
    let category = "other";
    if (/invalid json|model output|model response|workers ai|specialist result/.test(value)) {
      category = "model_output";
    } else if (/analytics_snapshot|topic_snapshot|control_center_snapshot|recommendation_snapshot|snapshot|event payload/.test(value)) {
      category = "source_data";
    } else if (/unavailable|not found|http \d{3}|fetch failed|could not fetch|status 0/.test(value)) {
      category = "source_unavailable";
    } else if (/insufficient|not enough|missing|no data|evidence|source/.test(value)) {
      category = "insufficient_evidence";
    }
    categories[category] += 1;
  }
  return Object.fromEntries(Object.entries(categories).filter(([, count]) => count > 0));
}

function safeObject(value, depth = 0) {
  if (!value || typeof value !== "object" || Array.isArray(value) || depth > 6) return false;
  for (const [key, child] of Object.entries(value)) {
    if (FORBIDDEN_KEY.test(key)) return false;
    if (child && typeof child === "object") {
      if (Array.isArray(child)) {
        if (child.length > 100 || child.some(item =>
          item && typeof item === "object" && !safeObject(item, depth + 1)
        )) return false;
      } else if (!safeObject(child, depth + 1)) return false;
    } else if (typeof child === "string" && child.length > 4000) {
      return false;
    }
  }
  return true;
}

const GITHUB_OIDC_ISSUER = "https://token.actions.githubusercontent.com";
const GITHUB_OIDC_AUDIENCE = "pettraffic-control-api";
const GITHUB_REPOSITORY = "Pershore/PetTraffic-AI";
const GITHUB_REPOSITORY_OWNER_ID = "124571174";
const GITHUB_REPOSITORY_ID = "1452256714";
const GITHUB_REF = "refs/heads/main";
// GitHub repositories created after 2026-07-15 use immutable owner/repository IDs in sub.
const GITHUB_SUBJECT = `repo:Pershore@${GITHUB_REPOSITORY_OWNER_ID}/PetTraffic-AI@${GITHUB_REPOSITORY_ID}:ref:${GITHUB_REF}`;

// Each workload has an independent identity. Never reuse the snapshot-sync role for task execution.
const GITHUB_OIDC_IDENTITIES = {
  snapshot_sync: {
    workflow_ref: "Pershore/PetTraffic-AI/.github/workflows/sync-control-api.yml@refs/heads/main",
    events: new Set(["workflow_run", "workflow_dispatch"]),
  },
  task_dispatcher: {
    workflow_ref: "Pershore/PetTraffic-AI/.github/workflows/dispatch-daily-suite.yml@refs/heads/main",
    events: new Set(["issue_comment"]),
  },
  task_runner: {
    workflow_ref: "Pershore/PetTraffic-AI/.github/workflows/run-readonly-tasks.yml@refs/heads/main",
    events: new Set(["schedule", "workflow_dispatch"]),
  },
};

function decodeBase64Url(value) {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const binary = atob(normalized + "=".repeat((4 - normalized.length % 4) % 4));
  return Uint8Array.from(binary, character => character.charCodeAt(0));
}

async function authorized(request) {
  const authorization = request.headers.get("authorization") || "";
  const match = authorization.match(/^Bearer\s+([A-Za-z0-9._~-]+)$/i);
  if (!match) return null;

  const parts = match[1].split(".");
  if (parts.length !== 3) return null;

  let header;
  let claims;
  try {
    header = JSON.parse(new TextDecoder().decode(decodeBase64Url(parts[0])));
    claims = JSON.parse(new TextDecoder().decode(decodeBase64Url(parts[1])));
  } catch {
    return null;
  }

  if (header.alg !== "RS256" || typeof header.kid !== "string") return null;
  const now = Math.floor(Date.now() / 1000);
  const audienceValid = claims.aud === GITHUB_OIDC_AUDIENCE ||
    (Array.isArray(claims.aud) && claims.aud.includes(GITHUB_OIDC_AUDIENCE));
  if (
    claims.iss !== GITHUB_OIDC_ISSUER ||
    !audienceValid ||
    claims.sub !== GITHUB_SUBJECT ||
    claims.repository !== GITHUB_REPOSITORY ||
    String(claims.repository_owner_id) !== GITHUB_REPOSITORY_OWNER_ID ||
    String(claims.repository_id) !== GITHUB_REPOSITORY_ID ||
    claims.ref !== GITHUB_REF ||
    !Number.isFinite(claims.exp) || claims.exp <= now ||
    (Number.isFinite(claims.nbf) && claims.nbf > now + 30)
  ) return null;

  const identity = Object.entries(GITHUB_OIDC_IDENTITIES).find(([, policy]) =>
    claims.workflow_ref === policy.workflow_ref && policy.events.has(claims.event_name)
  );
  if (!identity) return null;

  try {
    const jwksResponse = await fetch(`${GITHUB_OIDC_ISSUER}/.well-known/jwks`, {
      headers: { accept: "application/json" },
      cf: { cacheTtl: 300, cacheEverything: true },
    });
    if (!jwksResponse.ok) return null;
    const jwks = await jwksResponse.json();
    const jwk = jwks.keys?.find(key => key.kid === header.kid && key.kty === "RSA" && key.use === "sig");
    if (!jwk) return null;
    const publicKey = await crypto.subtle.importKey(
      "jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]
    );
    const valid = await crypto.subtle.verify(
      "RSASSA-PKCS1-v1_5",
      publicKey,
      decodeBase64Url(parts[2]),
      new TextEncoder().encode(`${parts[0]}.${parts[1]}`)
    );
    return valid ? identity[0] : null;
  } catch {
    return null;
  }
}

async function readJson(request) {
  const text = await request.text();
  if (new TextEncoder().encode(text).byteLength > MAX_BODY_BYTES) {
    return { error: "request_too_large" };
  }
  try {
    return { value: JSON.parse(text) };
  } catch {
    return { error: "invalid_json" };
  }
}

function validOrigin(request, env) {
  const origin = request.headers.get("origin");
  if (!origin) return null;
  return origin === env.ALLOWED_ORIGIN ? origin : false;
}

async function handle(request, env) {
  const url = new URL(request.url);
  const origin = validOrigin(request, env);
  if (origin === false) return response({ error: "origin_not_allowed" }, 403);
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "access-control-allow-origin": origin || "null",
        "access-control-allow-methods": "GET, POST, OPTIONS",
        "access-control-allow-headers": "authorization, content-type",
        "access-control-max-age": "600",
        vary: "Origin",
      },
    });
  }

  if (url.pathname === "/health" && request.method === "GET") {
    if (!env.DB) return response({ ok: false, error: "database_not_bound" }, 503, origin);
    try {
      await env.DB.prepare("SELECT 1 AS ok").first();
      await env.DB.prepare("SELECT 1 AS ok FROM control_core_runs LIMIT 1").first();
      await env.DB.prepare("SELECT 1 AS ok FROM control_core_memory LIMIT 1").first();
      const heartbeat = await env.DB.prepare(
        "SELECT checked_at, site_ok, site_status, database_ok FROM system_heartbeats ORDER BY checked_at DESC LIMIT 1"
      ).first();
      // Expose only aggregate execution metadata; never return prompts, model output or stored reports.
      const agentRun = await env.DB.prepare(
        "SELECT run_date, status, ai_calls, started_at, completed_at, error_code FROM agent_runs ORDER BY run_date DESC LIMIT 1"
      ).first();
      const controlCoreRun = await env.DB.prepare(
        "SELECT run_date, status, core_version, created_at, decision_json FROM control_core_runs ORDER BY created_at DESC LIMIT 1"
      ).first();
      const controlCoreMemory = await env.DB.prepare(
        "SELECT updated_at FROM control_core_memory WHERE memory_key = 'latest_control_decision' LIMIT 1"
      ).first();
      let decision = null;
      let decisionJsonStatus = "not_available";
      if (controlCoreRun) {
        try {
          decision = JSON.parse(controlCoreRun.decision_json);
          decisionJsonStatus = decision && typeof decision === "object" && !Array.isArray(decision) ? "valid" : "invalid_shape";
        } catch {
          decisionJsonStatus = "invalid_json";
        }
      }
      const controlCore = controlCoreRun ? {
        run_date: controlCoreRun.run_date,
        status: controlCoreRun.status,
        core_version: controlCoreRun.core_version,
        created_at: controlCoreRun.created_at,
        decision_json_status: decisionJsonStatus,
        recommendation_count: Array.isArray(decision?.recommendations) ? decision.recommendations.length : 0,
        evidence_gap_count: Array.isArray(decision?.evidence_gaps) ? decision.evidence_gaps.length : 0,
        specialist_statuses: decision?.specialist_statuses && typeof decision.specialist_statuses === "object"
          ? Object.fromEntries(Object.entries(decision.specialist_statuses)
            .filter(([id, status]) => ALLOWED_AGENTS.has(id) && typeof status === "string")
            .map(([id, status]) => [id, status.slice(0, 40)]))
          : {},
        evidence_gap_categories: summarizeEvidenceGapCategories(decision),
        memory_status: controlCoreMemory ? "present" : "missing",
        memory_updated_at: controlCoreMemory?.updated_at || null,
      } : {
        status: "not_started",
        decision_json_status: decisionJsonStatus,
        specialist_statuses: {},
        evidence_gap_categories: {},
        memory_status: controlCoreMemory ? "present" : "missing",
        memory_updated_at: controlCoreMemory?.updated_at || null,
      };
      return response({
        ok: true,
        service: "pettraffic-control-api",
        database: "connected",
        control_core_schema: "connected",
        control_core: controlCore,
        heartbeat: heartbeat ? {
          checked_at: heartbeat.checked_at,
          site_ok: Number(heartbeat.site_ok) === 1,
          site_status: Number(heartbeat.site_status),
          database_ok: Number(heartbeat.database_ok) === 1,
        } : null,
        agent_orchestration: agentRun ? {
          run_date: agentRun.run_date,
          status: agentRun.status,
          ai_calls: Number(agentRun.ai_calls),
          started_at: agentRun.started_at,
          completed_at: agentRun.completed_at,
          error_code: agentRun.status === "failed"
            ? (typeof agentRun.error_code === "string"
              ? agentRun.error_code.replace(/[^A-Za-z0-9_.-]/g, "_").slice(0, 80)
              : "agent_run_failed")
            : null,
        } : { status: "not_started" },
      }, 200, origin);
    } catch {
      return response({ ok: false, error: "database_unavailable" }, 503, origin);
    }
  }

  if (!url.pathname.startsWith("/v1/")) return response({ error: "not_found" }, 404, origin);
  if (!env.DB) return response({ error: "database_not_bound" }, 503, origin);

  if (url.pathname.startsWith("/v1/tasks")) {
    // Fail closed until both the dedicated OIDC roles and operator-side runtime flag are configured.
    if (env.TASK_API_ENABLED !== "true") return response({ error: "task_api_not_enabled" }, 503, origin);
    const identity = await authorized(request);
    if (!identity) return response({ error: "unauthorized" }, 401, origin);

    if (url.pathname === "/v1/tasks" && request.method === "POST") {
      if (identity !== "task_dispatcher") return response({ error: "forbidden_role" }, 403, origin);
      const parsed = await readJson(request);
      if (parsed.error) return response({ error: parsed.error }, parsed.error === "request_too_large" ? 413 : 400, origin);
      const body = parsed.value;
      const payload = body?.payload;
      const payloadIsExact = payload && typeof payload === "object" && !Array.isArray(payload) &&
        Object.keys(payload).length === 1 && payload.target === "public_site";
      const priority = Number(body?.priority ?? 3);
      if (
        !body ||
        body.type !== "check_site" ||
        body.agent !== "technical-seo" ||
        !payloadIsExact ||
        !safeObject(payload) ||
        !Number.isInteger(priority) || priority < 1 || priority > 5
      ) return response({ error: "invalid_task" }, 400, origin);

      // Avoid duplicate live site-check tasks if the owner repeats the same command.
      const pending = await env.DB.prepare(
        "SELECT id, status FROM tasks WHERE task_type = ? AND assigned_agent = ? " +
        "AND status IN ('queued', 'running') ORDER BY created_at ASC LIMIT 1"
      ).bind("check_site", "technical-seo").first();
      if (pending?.id) {
        return response({
          accepted: true,
          task_id: pending.id,
          status: pending.status,
          deduplicated: true,
        }, 202, origin);
      }

      const id = crypto.randomUUID();
      await env.DB.prepare(
        "INSERT INTO tasks (id, task_type, assigned_agent, priority, payload_json, status, created_at) " +
        "VALUES (?, 'check_site', 'technical-seo', ?, ?, 'queued', ?)"
      ).bind(id, priority, JSON.stringify(payload), new Date().toISOString()).run();
      return response({ accepted: true, task_id: id, status: "queued", deduplicated: false }, 202, origin);
    }

    if (url.pathname === "/v1/tasks/claim" && request.method === "POST") {
      if (identity !== "task_runner") return response({ error: "forbidden_role" }, 403, origin);
      const parsed = await readJson(request);
      if (parsed.error) return response({ error: parsed.error }, parsed.error === "request_too_large" ? 413 : 400, origin);
      const agent = parsed.value?.agent;
      if (agent !== "technical-seo") return response({ error: "invalid_agent" }, 400, origin);
      const now = new Date().toISOString();
      const expiredBefore = new Date(Date.now() - 30 * 60 * 1000).toISOString();
      await env.DB.prepare(
        "UPDATE tasks SET status = 'failed', completed_at = ? " +
        "WHERE status = 'running' AND claimed_at < ? AND attempt_count >= 3"
      ).bind(now, expiredBefore).run();
      const task = await env.DB.prepare(
        "UPDATE tasks SET status = 'running', claimed_by = ?, claimed_at = ?, attempt_count = attempt_count + 1 " +
        "WHERE id = (SELECT id FROM tasks WHERE (status = 'queued' OR (status = 'running' AND claimed_at < ?)) " +
        "AND attempt_count < 3 AND assigned_agent = ? AND task_type = 'check_site' " +
        "ORDER BY priority DESC, created_at ASC LIMIT 1) " +
        "RETURNING id, task_type, assigned_agent, priority, payload_json, created_at"
      ).bind(agent, now, expiredBefore, agent).first();
      if (!task) return response({ task: null }, 200, origin);
      return response({
        task: {
          id: task.id,
          type: task.task_type,
          assigned_agent: task.assigned_agent,
          priority: task.priority,
          payload: JSON.parse(task.payload_json),
          created_at: task.created_at,
        },
      }, 200, origin);
    }

    const completion = url.pathname.match(/^\/v1\/tasks\/([a-f0-9-]+)\/complete$/i);
    if (completion && request.method === "POST") {
      if (identity !== "task_runner") return response({ error: "forbidden_role" }, 403, origin);
      const parsed = await readJson(request);
      if (parsed.error) return response({ error: parsed.error }, parsed.error === "request_too_large" ? 413 : 400, origin);
      const body = parsed.value;
      if (
        !body ||
        body.agent !== "technical-seo" ||
        !["completed", "failed"].includes(body.status) ||
        !safeObject(body.result || {})
      ) return response({ error: "invalid_completion" }, 400, origin);
      const result = await env.DB.prepare(
        "UPDATE tasks SET status = ?, result_json = ?, completed_at = ? " +
        "WHERE id = ? AND status = 'running' AND claimed_by = 'technical-seo' "
      ).bind(body.status, JSON.stringify(body.result || {}), new Date().toISOString(), completion[1]).run();
      if (!result.meta?.changes) return response({ error: "task_not_owned_or_not_running" }, 409, origin);
      return response({ accepted: true, task_id: completion[1], status: body.status }, 200, origin);
    }

    return response({ error: "not_found" }, 404, origin);
  }

  if (url.pathname.startsWith("/v1/events")) {
    const identity = await authorized(request);
    if (!identity) return response({ error: "unauthorized" }, 401, origin);
    if (identity !== "snapshot_sync") return response({ error: "forbidden_role" }, 403, origin);

    if (url.pathname === "/v1/events" && request.method === "GET") {
      const kind = url.searchParams.get("kind");
      if (kind && !ALLOWED_EVENT_KINDS.has(kind)) return response({ error: "invalid_event_kind" }, 400, origin);
      const rows = await env.DB.prepare(
        "SELECT id, kind, payload_json, created_at FROM events WHERE (? IS NULL OR kind = ?) ORDER BY created_at DESC LIMIT 100"
      ).bind(kind, kind).all();
      return response({
        events: (rows.results || []).map(row => ({
          id: row.id,
          kind: row.kind,
          payload: JSON.parse(row.payload_json),
          created_at: row.created_at,
        })),
      }, 200, origin);
    }

    if (url.pathname === "/v1/events" && request.method === "POST") {
      const parsed = await readJson(request);
      if (parsed.error) return response({ error: parsed.error }, parsed.error === "request_too_large" ? 413 : 400, origin);
      const body = parsed.value;
      if (!body || !ALLOWED_EVENT_KINDS.has(body.kind) || !safeObject(body.payload)) {
        return response({ error: "invalid_event_payload" }, 400, origin);
      }
      const sourceRunId = typeof body.payload.run_id === "string" ? body.payload.run_id.trim() : "";
      if (sourceRunId) {
        const existing = await env.DB.prepare(
          "SELECT id FROM events WHERE kind = ? AND json_extract(payload_json, '$.run_id') = ? ORDER BY created_at ASC LIMIT 1"
        ).bind(body.kind, sourceRunId).first();
        if (existing?.id) {
          return response({ accepted: true, id: existing.id, deduplicated: true }, 202, origin);
        }
      }

      const id = crypto.randomUUID();
      await env.DB.prepare(
        "INSERT INTO events (id, kind, payload_json, created_at) VALUES (?, ?, ?, ?)"
      ).bind(id, body.kind, JSON.stringify(body.payload), new Date().toISOString()).run();
      return response({ accepted: true, id, deduplicated: false }, 202, origin);
    }
  }

  return response({ error: "not_found" }, 404, origin);
}

async function runScheduledHealthCheck(env) {
  const checkedAt = new Date().toISOString();
  let siteStatus = 0;
  let siteOk = 0;
  try {
    const siteResponse = await fetch("https://pettraffic-ai.pages.dev/", {
      method: "GET",
      redirect: "follow",
      headers: { "user-agent": "PetTraffic-ControlCenter/1.0" },
    });
    siteStatus = siteResponse.status;
    siteOk = siteResponse.ok ? 1 : 0;
  } catch {
    siteStatus = 0;
    siteOk = 0;
  }

  let databaseOk = 0;
  try {
    await env.DB.prepare("SELECT 1 AS ok").first();
    databaseOk = 1;
    await env.DB.prepare(
      "INSERT INTO system_heartbeats (checked_at, site_ok, site_status, database_ok) VALUES (?, ?, ?, ?)"
    ).bind(checkedAt, siteOk, siteStatus, databaseOk).run();

    // Keep a rolling 30-day operational heartbeat history.
    if (new Date().getUTCHours() === 0 && new Date().getUTCMinutes() < 15) {
      await env.DB.prepare(
        "DELETE FROM system_heartbeats WHERE checked_at < ?"
      ).bind(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()).run();
    }
  } catch (error) {
    console.error("PetTraffic scheduled health check could not write heartbeat:", error);
  }
}

async function runAgentOrchestrationWhenReady(env, controller) {
  try {
    if (!(await shouldRunAgentOrchestration(env, controller))) return;
    const result = await runAgentOrchestration(env);
    if (result?.completed) {
      console.info("PetTraffic daily AI orchestration completed and persisted.", {
        run_date: result.run_date,
        ai_calls: result.ai_calls,
      });
    } else if (result?.error) {
      console.error("PetTraffic daily AI orchestration failed:", result.error);
    }
  } catch (error) {
    const message = String(error?.message || "readiness_check_failed").slice(0, 120);
    console.error("PetTraffic daily AI orchestration readiness check failed:", message);
  }
}

export default {
  async fetch(request, env) {
    try {
      return await handle(request, env);
    } catch {
      return response({ error: "internal_error" }, 500);
    }
  },
  async scheduled(controller, env, ctx) {
    if (isAgentScheduledEvent(controller)) {
      ctx.waitUntil(runAgentOrchestrationWhenReady(env, controller));
      return;
    }
    if (isAgentCatchUpEvent(controller)) {
      ctx.waitUntil(Promise.all([
        runScheduledHealthCheck(env),
        runAgentOrchestrationWhenReady(env, controller),
      ]));
      return;
    }
    ctx.waitUntil(runScheduledHealthCheck(env));
  },
};
