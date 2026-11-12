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
const FORBIDDEN_KEY = /(^|_)(email|ip|ip_address|user_id|client_id|search_query|query_text|token|secret|password|authorization|cookie)(_|$)/i;

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

async function authorized(request, env) {
  const expected = env.API_TOKEN;
  const supplied = (request.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  if (!expected) return false;
  const encoder = new TextEncoder();
  const [a, b] = await Promise.all([
    crypto.subtle.digest("SHA-256", encoder.encode(expected)),
    crypto.subtle.digest("SHA-256", encoder.encode(supplied)),
  ]);
  const left = new Uint8Array(a);
  const right = new Uint8Array(b);
  let difference = 0;
  for (let i = 0; i < left.length; i++) difference |= left[i] ^ right[i];
  return difference === 0 && supplied.length > 0;
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
      return response({ ok: true, service: "pettraffic-control-api", database: "connected" }, 200, origin);
    } catch {
      return response({ ok: false, error: "database_unavailable" }, 503, origin);
    }
  }

  if (!url.pathname.startsWith("/v1/")) return response({ error: "not_found" }, 404, origin);
  if (!env.DB) return response({ error: "database_not_bound" }, 503, origin);
  if (!env.API_TOKEN) return response({ error: "api_token_not_configured" }, 503, origin);
  if (!(await authorized(request, env))) return response({ error: "unauthorized" }, 401, origin);

  if (url.pathname === "/v1/events" && request.method === "POST") {
    const parsed = await readJson(request);
    if (parsed.error) return response({ error: parsed.error }, 413, origin);
    const body = parsed.value;
    if (!body || !ALLOWED_EVENT_KINDS.has(body.kind) || !safeObject(body.payload)) {
      return response({ error: "invalid_event_payload" }, 400, origin);
    }
    const id = crypto.randomUUID();
    await env.DB.prepare(
      "INSERT INTO events (id, kind, payload_json, created_at) VALUES (?, ?, ?, ?)"
    ).bind(id, body.kind, JSON.stringify(body.payload), new Date().toISOString()).run();
    return response({ accepted: true, id }, 202, origin);
  }

  if (url.pathname === "/v1/tasks" && request.method === "POST") {
    const parsed = await readJson(request);
    if (parsed.error) return response({ error: parsed.error }, 413, origin);
    const body = parsed.value;
    const priority = Number(body?.priority ?? 3);
    if (
      !body ||
      !ALLOWED_TASK_TYPES.has(body.type) ||
      !ALLOWED_AGENTS.has(body.agent) ||
      !Number.isInteger(priority) ||
      priority < 1 || priority > 5 ||
      !safeObject(body.payload || {})
    ) return response({ error: "invalid_task" }, 400, origin);

    const id = crypto.randomUUID();
    await env.DB.prepare(
      "INSERT INTO tasks (id, task_type, assigned_agent, priority, payload_json, status, created_at) VALUES (?, ?, ?, ?, ?, 'queued', ?)"
    ).bind(id, body.type, body.agent, priority, JSON.stringify(body.payload || {}), new Date().toISOString()).run();
    return response({ accepted: true, task_id: id, status: "queued" }, 202, origin);
  }

  if (url.pathname === "/v1/tasks/claim" && request.method === "POST") {
    const parsed = await readJson(request);
    if (parsed.error) return response({ error: parsed.error }, 413, origin);
    const agent = parsed.value?.agent;
    if (!ALLOWED_AGENTS.has(agent)) return response({ error: "invalid_agent" }, 400, origin);
    const task = await env.DB.prepare(
      "UPDATE tasks SET status = 'running', claimed_by = ?, claimed_at = ? " +
      "WHERE id = (SELECT id FROM tasks WHERE status = 'queued' AND assigned_agent IN (?, 'coordinator') " +
      "ORDER BY priority DESC, created_at ASC LIMIT 1) RETURNING id, task_type, assigned_agent, priority, payload_json, created_at"
    ).bind(agent, new Date().toISOString(), agent).first();
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
    const parsed = await readJson(request);
    if (parsed.error) return response({ error: parsed.error }, 413, origin);
    const body = parsed.value;
    if (
      !body ||
      !ALLOWED_AGENTS.has(body.agent) ||
      !["completed", "failed"].includes(body.status) ||
      !safeObject(body.result || {})
    ) return response({ error: "invalid_completion" }, 400, origin);
    const result = await env.DB.prepare(
      "UPDATE tasks SET status = ?, result_json = ?, completed_at = ? " +
      "WHERE id = ? AND status = 'running' AND claimed_by = ?"
    ).bind(body.status, JSON.stringify(body.result || {}), new Date().toISOString(), completion[1], body.agent).run();
    if (!result.meta?.changes) return response({ error: "task_not_owned_or_not_running" }, 409, origin);
    return response({ accepted: true, task_id: completion[1], status: body.status }, 200, origin);
  }

  return response({ error: "not_found" }, 404, origin);
}

export default {
  async fetch(request, env) {
    try {
      return await handle(request, env);
    } catch {
      return response({ error: "internal_error" }, 500);
    }
  },
};
