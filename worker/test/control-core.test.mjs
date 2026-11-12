import test from "node:test";
import assert from "node:assert/strict";
import { buildControlDecision, persistControlDecision, CONTROL_CORE_VERSION } from "../src/control-core.mjs";

test("control core creates a bounded read-only decision", () => {
  const decision = buildControlDecision({
    date_utc: "2026-11-13",
    generated_at: "2026-11-13T08:20:00.000Z",
    specialists: { analytics: { status: "reviewed" }, topics: { status: "needs_data" } },
    coordinator: {
      findings: ["Traffic snapshot is available."],
      recommendations: ["Review sitemap coverage."],
      evidence_gaps: ["No indexed URL evidence yet."],
    },
  });
  assert.equal(decision.core_version, CONTROL_CORE_VERSION);
  assert.equal(decision.status, "needs_evidence");
  assert.equal(decision.specialist_count, 2);
  assert.equal(decision.requires_human_approval, true);
  assert.ok(decision.policy.blocked.includes("publish_content"));
  assert.ok(decision.policy.blocked.includes("modify_aro_vet"));
  assert.deepEqual(decision.recommendations, ["Review sitemap coverage."]);
});

test("model-supplied actions cannot override deterministic policy", () => {
  const decision = buildControlDecision({
    date_utc: "2026-11-13",
    coordinator: { findings: "invalid", recommendations: [1, "Safe suggestion"], actions: ["publish_content"] },
  });
  assert.deepEqual(decision.findings, []);
  assert.deepEqual(decision.recommendations, ["Safe suggestion"]);
  assert.ok(decision.policy.blocked.includes("publish_content"));
  assert.equal("actions" in decision, false);
});

test("control core persists decision and compact memory in D1", async () => {
  const writes = [];
  const env = { DB: { prepare(sql) { return { bind(...values) { return { run: async () => { writes.push({ sql, values }); return { meta: { changes: 1 } }; } }; } }; } } };
  const decision = buildControlDecision({ date_utc: "2026-11-13", specialists: {}, coordinator: {} });
  const result = await persistControlDecision(env, decision);
  assert.equal(result.persisted, true);
  assert.equal(writes.length, 2);
  assert.ok(writes[0].sql.includes("control_core_runs"));
  assert.ok(writes[1].sql.includes("control_core_memory"));
  assert.equal(JSON.parse(writes[1].values[1]).last_run_date, "2026-11-13");
});

test("control core refuses persistence without D1", async () => {
  await assert.rejects(() => persistControlDecision({}, { run_date: "2026-11-13" }), /database_missing/);
});

test("specialist evidence gaps cannot be hidden by an empty coordinator response", () => {
  const decision = buildControlDecision({
    date_utc: "2026-11-13",
    specialists: { analytics: { status: "needs_data", evidence_gaps: ["GA4 snapshot missing"] } },
    coordinator: { findings: [], recommendations: [], evidence_gaps: [] },
  });
  assert.equal(decision.status, "needs_evidence");
  assert.ok(decision.evidence_gaps.some(gap => gap.includes("GA4 snapshot missing")));
});

test("control core rejects invalid dates and malformed persistence payloads", async () => {
  const decision = buildControlDecision({ date_utc: "not-a-date", coordinator: {} });
  await assert.rejects(() => persistControlDecision({ DB: { prepare() { throw new Error("should_not_prepare"); } } }, decision), /run_date_invalid/);
});
