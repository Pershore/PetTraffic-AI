import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.mjs";

const env = {
  API_TOKEN: "test-secret",
  ALLOWED_ORIGIN: "https://pettraffic-ai.pages.dev",
  DB: {
    prepare() {
      return {
        first: async () => ({ ok: 1 }),
        bind() {
          return {
            run: async () => ({ meta: { changes: 1 } }),
            first: async () => null,
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

test("versioned endpoints reject missing bearer token", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/events", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ kind: "analytics_snapshot", payload: {} }),
  }), env);
  assert.equal(response.status, 401);
  assert.deepEqual(await response.json(), { error: "unauthorized" });
});

test("versioned endpoints reject an unconfigured API token", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/events", {
    method: "POST",
    headers: { authorization: "Bearer test-secret", "content-type": "application/json" },
    body: JSON.stringify({ kind: "analytics_snapshot", payload: {} }),
  }), { ...env, API_TOKEN: undefined });
  assert.equal(response.status, 503);
});

test("unknown event kinds are rejected", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/events", {
    method: "POST",
    headers: { authorization: "Bearer test-secret", "content-type": "application/json" },
    body: JSON.stringify({ kind: "arbitrary", payload: {} }),
  }), env);
  assert.equal(response.status, 400);
});

test("potential personal data and secrets are rejected from event payloads", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/events", {
    method: "POST",
    headers: { authorization: "Bearer test-secret", "content-type": "application/json" },
    body: JSON.stringify({ kind: "analytics_snapshot", payload: { user_id: "visitor-1" } }),
  }), env);
  assert.equal(response.status, 400);
});

test("task creation rejects unknown task types", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/tasks", {
    method: "POST",
    headers: { authorization: "Bearer test-secret", "content-type": "application/json" },
    body: JSON.stringify({ type: "publish_article", agent: "content-review", payload: {} }),
  }), env);
  assert.equal(response.status, 400);
});

test("CORS rejects origins other than the PetTraffic site", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/events", {
    method: "POST",
    headers: {
      origin: "https://malicious.example",
      authorization: "Bearer test-secret",
      "content-type": "application/json",
    },
    body: JSON.stringify({ kind: "analytics_snapshot", payload: {} }),
  }), env);
  assert.equal(response.status, 403);
});
