import test from "node:test";
import assert from "node:assert/strict";
import { generateKeyPairSync, createSign } from "node:crypto";
import worker from "../src/index.mjs";

const { publicKey, privateKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
const jwk = { ...publicKey.export({ format: "jwk" }), kid: "test-key", use: "sig", alg: "RS256" };
function base64url(value) { return Buffer.from(value).toString("base64url"); }
function oidcToken(overrides = {}) {
  const header = base64url(JSON.stringify({ alg: "RS256", typ: "JWT", kid: "test-key" }));
  const claims = base64url(JSON.stringify({
    iss: "https://token.actions.githubusercontent.com",
    aud: "pettraffic-control-api",
    sub: "repo:Pershore/PetTraffic-AI:ref:refs/heads/main",
    repository: "Pershore/PetTraffic-AI",
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
    prepare() {
      return {
        first: async () => ({ ok: 1 }),
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
  });
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
        payload: { generated_at: "2026-11-12T10:00:00Z", metrics: { sessions: 4, active_users: 2 } },
      }),
    }), env);
    assert.equal(response.status, 202);
    assert.equal((await response.json()).accepted, true);
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
