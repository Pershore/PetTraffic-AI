import test from "node:test";
import assert from "node:assert/strict";
import { generateKeyPairSync, createSign } from "node:crypto";
import worker from "../src/index.mjs";
import { callModel, extractResponseText, parseResult } from "../src/agents.mjs";

const { publicKey, privateKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
const jwk = { ...publicKey.export({ format: "jwk" }), kid: "test-key", use: "sig", alg: "RS256" };
function base64url(value) { return Buffer.from(value).toString("base64url"); }
function oidcToken(overrides = {}) {
  const header = base64url(JSON.stringify({ alg: "RS256", typ: "JWT", kid: "test-key" }));
  const claims = base64url(JSON.stringify({
    iss: "https://token.actions.githubusercontent.com",
    aud: "pettraffic-control-api",
    sub: "repo:Pershore@124571174/PetTraffic-AI@1452256714:ref:refs/heads/main",
    repository: "Pershore/PetTraffic-AI",
    repository_owner_id: "124571174",
    repository_id: "1452256714",
    ref: "refs/heads/main",
    workflow_ref: "Pershore/PetTraffic-AI/.github/workflows/sync-control-api.yml@refs/heads/main",
    event_name: "workflow_run",
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 300,
    ...overrides,
  }));
  const unsigned = header + "." + claims;
  const signer = createSign("RSA-SHA256");
  signer.update(unsigned); signer.end();
  return unsigned + "." + signer.sign(privateKey).toString("base64url");
}
async function withOidcJwks(callback) {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response(JSON.stringify({ keys: [jwk] }), { status: 200 });
  try { return await callback(); } finally { globalThis.fetch = originalFetch; }
}

globalThis.fetch = async () => new Response(JSON.stringify({ keys: [jwk] }), { status: 200 });
const env = {
  ALLOWED_ORIGIN: "https://pettraffic-ai.pages.dev",
  DB: {
    prepare(sql) {
      return {
        first: async () => sql.includes("system_heartbeats") || sql.includes("agent_runs") || sql.includes("SELECT run_date, status, core_version") || sql.includes("WHERE memory_key = 'latest_control_decision'") ? null : ({ ok: 1 }),
        bind() {
          return {
            run: async () => ({ meta: { changes: 1 } }),
            first: async () => null,
            all: async () => ({ results: [] }),
          };
        },
      };
    },
  },
};

test("health endpoint confirms database connectivity without exposing secrets", async () => {
  const response = await worker.fetch(new Request("https://api.example/health"), env);
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), {
    ok: true,
    service: "pettraffic-control-api",
    database: "connected",
    control_core_schema: "connected",
    control_core: { status: "not_started", decision_json_status: "not_available", memory_status: "missing", memory_updated_at: null },
    heartbeat: null,
    agent_orchestration: { status: "not_started" },
  });
});

test("health endpoint exposes the latest scheduled heartbeat", async () => {
  const heartbeat = {
    checked_at: "2026-11-12T10:15:00.000Z",
    site_ok: 1,
    site_status: 200,
    database_ok: 1,
  };
  const heartbeatEnv = {
    ...env,
    DB: {
      prepare(sql) {
        return {
          first: async () => sql.includes("system_heartbeats") ? heartbeat : sql.includes("agent_runs") || sql.includes("SELECT run_date, status, core_version") || sql.includes("WHERE memory_key = 'latest_control_decision'") ? null : ({ ok: 1 }),
        };
      },
    },
  };
  const response = await worker.fetch(new Request("https://api.example/health"), heartbeatEnv);
  assert.equal(response.status, 200);
  assert.deepEqual((await response.json()).heartbeat, {
    checked_at: heartbeat.checked_at,
    site_ok: true,
    site_status: 200,
    database_ok: true,
  });
});

test("health endpoint exposes only aggregate AI orchestration execution metadata", async () => {
  const agentRun = {
    run_date: "2026-11-13",
    status: "failed",
    ai_calls: 2,
    started_at: "2026-11-13T08:20:00.000Z",
    completed_at: "2026-11-13T08:20:30.000Z",
    error_code: "model error: model not available",
  };
  const agentEnv = {
    ...env,
    DB: {
      prepare(sql) {
        return {
          first: async () => sql.includes("agent_runs") ? agentRun : null,
        };
      },
    },
  };
  const response = await worker.fetch(new Request("https://api.example/health"), agentEnv);
  assert.equal(response.status, 200);
  assert.deepEqual((await response.json()).agent_orchestration, {
    ...agentRun,
    error_code: "model_error__model_not_available",
  });
});

test("health endpoint reports control-core persistence without exposing decision text", async () => {
  const coreRun = {
    run_date: "2026-11-13",
    status: "needs_evidence",
    core_version: "1.0.0",
    created_at: "2026-11-13T08:21:00.000Z",
    decision_json: JSON.stringify({
      recommendations: ["Review sitemap."],
      evidence_gaps: ["GA4 unavailable"],
    }),
  };
  const coreMemory = { updated_at: "2026-11-13T08:21:00.000Z" };
  const coreEnv = {
    ...env,
    DB: {
      prepare(sql) {
        return {
          first: async () => {
            if (sql.includes("SELECT run_date, status, core_version")) return coreRun;
            if (sql.includes("WHERE memory_key = 'latest_control_decision'")) return coreMemory;
            return null;
          },
        };
      },
    },
  };
  const response = await worker.fetch(new Request("https://api.example/health"), coreEnv);
  assert.equal(response.status, 200);
  const body = await response.json();
  assert.deepEqual(body.control_core, {
    run_date: coreRun.run_date,
    status: coreRun.status,
    core_version: coreRun.core_version,
    created_at: coreRun.created_at,
    decision_json_status: "valid",
    recommendation_count: 1,
    evidence_gap_count: 1,
    memory_status: "present",
    memory_updated_at: coreMemory.updated_at,
  });
  assert.doesNotMatch(JSON.stringify(body), /Review sitemap|GA4 unavailable/);
});

test("health endpoint reports malformed persisted decision JSON without failing the whole health response", async () => {
  const coreRun = {
    run_date: "2026-11-13",
    status: "needs_evidence",
    core_version: "1.0.0",
    created_at: "2026-11-13T08:21:00.000Z",
    decision_json: '{"recommendations":',
  };
  const coreEnv = {
    ...env,
    DB: {
      prepare(sql) {
        return {
          first: async () => {
            if (sql.includes("SELECT run_date, status, core_version")) return coreRun;
            if (sql.includes("WHERE memory_key = 'latest_control_decision'")) return { updated_at: "2026-11-13T08:21:00.000Z" };
            return null;
          },
        };
      },
    },
  };
  const response = await worker.fetch(new Request("https://api.example/health"), coreEnv);
  assert.equal(response.status, 200);
  const body = await response.json();
  assert.equal(body.control_core.decision_json_status, "invalid_json");
  assert.equal(body.control_core.recommendation_count, 0);
  assert.equal(body.control_core.memory_status, "present");
});

test("versioned endpoints reject requests without GitHub OIDC identity", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/events", {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ kind: "analytics_snapshot", payload: {} }),
  }), env);
  assert.equal(response.status, 401);
});
test("versioned endpoints reject OIDC tokens with the wrong audience", async () => {
  await withOidcJwks(async () => {
    const response = await worker.fetch(new Request("https://api.example/v1/events", {
      headers: { authorization: "Bearer " + oidcToken({ aud: "wrong-audience" }) },
    }), env);
    assert.equal(response.status, 401);
  });
});
test("versioned endpoints reject OIDC tokens from another repository", async () => {
  await withOidcJwks(async () => {
    const response = await worker.fetch(new Request("https://api.example/v1/events", {
      headers: { authorization: "Bearer " + oidcToken({ repository: "someone/else" }) },
    }), env);
    assert.equal(response.status, 401);
  });
});

test("versioned endpoints reject legacy mutable repository subjects", async () => {
  await withOidcJwks(async () => {
    const response = await worker.fetch(new Request("https://api.example/v1/events", {
      headers: {
        authorization: "Bearer " + oidcToken({
          sub: "repo:Pershore/PetTraffic-AI:ref:refs/heads/main",
        }),
      },
    }), env);
    assert.equal(response.status, 401);
  });
});

test("versioned endpoints reject mismatched immutable repository IDs", async () => {
  await withOidcJwks(async () => {
    const response = await worker.fetch(new Request("https://api.example/v1/events", {
      headers: {
        authorization: "Bearer " + oidcToken({ repository_id: "999999" }),
      },
    }), env);
    assert.equal(response.status, 401);
  });
});

test("versioned endpoints reject OIDC tokens from another workflow", async () => {
  await withOidcJwks(async () => {
    const response = await worker.fetch(new Request("https://api.example/v1/events", {
      headers: { authorization: "Bearer " + oidcToken({ workflow_ref: "Pershore/PetTraffic-AI/.github/workflows/other.yml@refs/heads/main" }) },
    }), env);
    assert.equal(response.status, 401);
  });
});

test("versioned endpoints reject invalid JWT signatures", async () => {
  await withOidcJwks(async () => {
    const valid = oidcToken();
    const index = Math.floor(valid.length / 2);
    const tampered = valid.slice(0, index) + (valid[index] === "A" ? "B" : "A") + valid.slice(index + 1);
    const response = await worker.fetch(new Request("https://api.example/v1/events", {
      headers: { authorization: "Bearer " + tampered },
    }), env);
    assert.equal(response.status, 401);
  });
});

test("event history can be read using a verified GitHub OIDC identity", async () => {
  await withOidcJwks(async () => {
    const response = await worker.fetch(new Request("https://api.example/v1/events", {
      headers: { authorization: "Bearer " + oidcToken() },
    }), env);
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { events: [] });
  });
});
test("valid aggregate snapshots can be accepted using GitHub OIDC", async () => {
  await withOidcJwks(async () => {
    const response = await worker.fetch(new Request("https://api.example/v1/events", {
      method: "POST",
      headers: { authorization: "Bearer " + oidcToken(), "content-type": "application/json" },
      body: JSON.stringify({
        kind: "analytics_snapshot",
        payload: { run_id: "run-1", generated_at: "2026-11-12T10:00:00Z", metrics: { sessions: 4, active_users: 2 } },
      }),
    }), env);
    assert.equal(response.status, 202);
    const body = await response.json();
    assert.equal(body.accepted, true);
    assert.equal(body.deduplicated, false);
  });
});

test("event ingestion deduplicates repeated attempts of the same source workflow run", async () => {
  await withOidcJwks(async () => {
    let storedId = null;
    let writes = 0;
    const idempotentEnv = {
      ...env,
      DB: {
        prepare(sql) {
          return {
            first: async () => sql.includes("json_extract") ? (storedId ? { id: storedId } : null) : ({ ok: 1 }),
            bind(...values) {
              return {
                first: async () => sql.includes("json_extract") ? (storedId ? { id: storedId } : null) : null,
                run: async () => {
                  if (sql.includes("INSERT INTO events")) {
                    writes += 1;
                    storedId = values[0];
                  }
                  return { meta: { changes: 1 } };
                },
                all: async () => ({ results: [] }),
              };
            },
          };
        },
      },
    };
    const send = generatedAt => worker.fetch(new Request("https://api.example/v1/events", {
      method: "POST",
      headers: { authorization: "Bearer " + oidcToken(), "content-type": "application/json" },
      body: JSON.stringify({
        kind: "analytics_snapshot",
        payload: { run_id: "same-source-run", generated_at: generatedAt, metrics: { sessions: 4 } },
      }),
    }), idempotentEnv);

    const first = await send("2026-11-12T10:00:00Z");
    const firstBody = await first.json();
    const second = await send("2026-11-12T10:05:00Z");
    const secondBody = await second.json();
    assert.equal(first.status, 202);
    assert.equal(second.status, 202);
    assert.equal(firstBody.id, secondBody.id);
    assert.equal(firstBody.deduplicated, false);
    assert.equal(secondBody.deduplicated, true);
    assert.equal(writes, 1);
  });
});
test("unknown event kinds are rejected", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/events", {
    method: "POST",
    headers: { authorization: "Bearer " + oidcToken(), "content-type": "application/json" },
    body: JSON.stringify({ kind: "arbitrary", payload: {} }),
  }), env);
  assert.equal(response.status, 400);
});

test("potential personal data and secrets are rejected from event payloads", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/events", {
    method: "POST",
    headers: { authorization: "Bearer " + oidcToken(), "content-type": "application/json" },
    body: JSON.stringify({ kind: "analytics_snapshot", payload: { user_id: "visitor-1" } }),
  }), env);
  assert.equal(response.status, 400);
});

test("task API remains disabled until a dedicated agent identity is configured", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/tasks", {
    method: "POST",
    headers: { authorization: "Bearer " + oidcToken(), "content-type": "application/json" },
    body: JSON.stringify({
      type: "check_site",
      agent: "technical-seo",
      priority: 4,
      payload: { target: "sitemap" },
    }),
  }), env);
  assert.equal(response.status, 503);
  assert.deepEqual(await response.json(), { error: "task_api_not_enabled" });
});

test("task claim route is unavailable to the snapshot sync identity", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/tasks/claim", {
    method: "POST",
    headers: { authorization: "Bearer " + oidcToken(), "content-type": "application/json" },
    body: JSON.stringify({ agent: "coordinator" }),
  }), env);
  assert.equal(response.status, 503);
  assert.deepEqual(await response.json(), { error: "task_api_not_enabled" });
});

test("CORS rejects origins other than the PetTraffic site", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/events", {
    method: "POST",
    headers: {
      origin: "https://malicious.example",
      authorization: "Bearer " + oidcToken(),
      "content-type": "application/json",
    },
    body: JSON.stringify({ kind: "analytics_snapshot", payload: {} }),
  }), env);
  assert.equal(response.status, 403);
});


test("scheduled health check records site and D1 status", async () => {
  const statements = [];
  const scheduledEnv = {
    DB: {
      prepare(sql) {
        statements.push(sql);
        return {
          first: async () => ({ ok: 1 }),
          bind(...values) {
            return { run: async () => ({ meta: { changes: 1 }, values }) };
          },
        };
      },
    },
  };
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response("ok", { status: 200 });
  let scheduledPromise;
  try {
    await worker.scheduled(
      { cron: "*/15 * * * *" },
      scheduledEnv,
      { waitUntil(promise) { scheduledPromise = promise; } },
    );
    await scheduledPromise;
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.ok(statements.some(sql => sql.includes("SELECT 1 AS ok")));
  assert.ok(statements.some(sql => sql.includes("INSERT INTO system_heartbeats")));
});

test("health endpoint fails closed when control-core D1 migrations are missing", async () => {
  const brokenEnv = {
    ...env,
    DB: {
      prepare(sql) {
        return {
          first: async () => {
            if (sql.includes("control_core_runs") || sql.includes("control_core_memory")) {
              throw new Error("no such table");
            }
            return sql.includes("system_heartbeats") ? null : ({ ok: 1 });
          },
        };
      },
    },
  };
  const response = await worker.fetch(new Request("https://api.example/health"), brokenEnv);
  assert.equal(response.status, 503);
  assert.deepEqual(await response.json(), { ok: false, error: "database_unavailable" });
});

const agentValidJson = JSON.stringify({
  status: "reviewed",
  findings: ["Sitemap is pending."],
  recommendations: ["Check crawl discovery."],
  evidence_gaps: [],
});

test("extracts text from the GPT-OSS Responses API output array", () => {
  const result = {
    output: [{
      type: "message",
      content: [{ type: "output_text", text: agentValidJson }],
    }],
  };
  assert.equal(extractResponseText(result), agentValidJson);
});

test("supports the native Workers AI response string shape", () => {
  assert.equal(extractResponseText({ response: agentValidJson }), agentValidJson);
});

test("supports OpenAI chat completion response shape as a compatibility fallback", () => {
  assert.equal(extractResponseText({
    choices: [{ message: { content: agentValidJson } }],
  }), agentValidJson);
});

test("parses fenced JSON and JSON surrounded by short prose", () => {
  assert.equal(parseResult("Result:\n\x60\x60\x60json\n" + agentValidJson + "\n\x60\x60\x60").status, "reviewed");
});

test("empty or incomplete model output becomes a bounded evidence gap instead of throwing", () => {
  const empty = parseResult("");
  const incomplete = parseResult('{"status":"reviewed"');
  assert.equal(empty.status, "invalid_response");
  assert.equal(incomplete.status, "invalid_json");
  assert.equal(empty.findings.length, 0);
  assert.equal(incomplete.recommendations.length, 0);
  assert.equal(empty.requires_human_approval, true);
});

test("GPT-OSS is called through Responses API with low reasoning and bounded output", async () => {
  let model;
  let request;
  const result = await callModel({
    AI: {
      run: async (selectedModel, body) => {
        model = selectedModel;
        request = body;
        return {
          output: [{
            type: "message",
            content: [{ type: "output_text", text: agentValidJson }],
          }],
        };
      },
    },
  }, "system prompt", "source data");

  assert.equal(model, "@cf/openai/gpt-oss-20b");
  assert.equal(request.input[0].role, "system");
  assert.match(request.input[0].content, /^system prompt\\n\\nIšvesties ribos:/);
  assert.deepEqual(request.input[1], { role: "user", content: "source data" });
  assert.deepEqual(request.reasoning, { effort: "low" });
  assert.equal(request.max_output_tokens, 1024);
  assert.equal(result.status, "reviewed");
});

test("AI request errors are converted into an explicit evidence gap", async () => {
  const result = await callModel({
    AI: { run: async () => { throw new Error("internal model detail"); } },
  }, "system", "input");
  assert.equal(result.status, "unavailable");
  assert.match(result.evidence_gaps[0], /Workers AI request failed/);
  assert.doesNotMatch(JSON.stringify(result), /internal model detail/);
});
