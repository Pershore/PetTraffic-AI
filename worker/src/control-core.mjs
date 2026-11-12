export const CONTROL_CORE_VERSION = "1.0.0";

const BLOCKED_ACTIONS = [
  "publish_content",
  "edit_live_site",
  "edit_dns",
  "modify_aro_vet",
  "spend_money",
  "change_cloudflare_permissions",
  "execute_arbitrary_code",
];

function safeStrings(value, limit = 10) {
  return Array.isArray(value)
    ? value.filter(item => typeof item === "string").slice(0, limit).map(item => item.slice(0, 400))
    : [];
}

/**
 * Convert specialist output into a deterministic governance decision.
 * The model may recommend; only the policy layer can describe permitted actions.
 */
export function buildControlDecision(report) {
  const specialists = report?.specialists && typeof report.specialists === "object"
    ? report.specialists
    : {};
  const coordinator = report?.coordinator && typeof report.coordinator === "object"
    ? report.coordinator
    : {};
  const findings = safeStrings(coordinator.findings);
  const recommendations = safeStrings(coordinator.recommendations, 5);
  const evidenceGaps = safeStrings(coordinator.evidence_gaps);
  const specialistStatuses = Object.fromEntries(
    Object.entries(specialists).map(([id, result]) => [
      id,
      typeof result?.status === "string" ? result.status.slice(0, 40) : "unknown",
    ]),
  );

  return {
    core_version: CONTROL_CORE_VERSION,
    run_date: String(report?.date_utc || "").slice(0, 10),
    generated_at: typeof report?.generated_at === "string" ? report.generated_at : new Date().toISOString(),
    status: evidenceGaps.length ? "needs_evidence" : "reviewed",
    specialist_count: Object.keys(specialists).length,
    specialist_statuses: specialistStatuses,
    findings,
    recommendations,
    evidence_gaps: evidenceGaps,
    policy: {
      mode: "advisory_read_only",
      allowed: ["read_aggregate_snapshots", "read_public_site", "run_bounded_analysis", "store_project_memory", "create_reviewable_code_pull_request"],
      blocked: BLOCKED_ACTIONS,
      human_approval_required_for: ["content_publication", "production_site_changes", "infrastructure_changes", "external_spending", "security_permission_changes"],
    },
    requires_human_approval: true,
  };
}

/** Persist a compact, privacy-filtered control decision and rolling memory in D1. */
export async function persistControlDecision(env, decision) {
  if (!env?.DB) throw new Error("control_core_database_missing");
  if (!decision?.run_date) throw new Error("control_core_run_date_missing");

  const createdAt = new Date().toISOString();
  const decisionJson = JSON.stringify(decision);
  const memory = {
    core_version: CONTROL_CORE_VERSION,
    last_run_date: decision.run_date,
    last_status: decision.status,
    specialist_count: decision.specialist_count,
    open_recommendations: decision.recommendations.length,
    evidence_gaps: decision.evidence_gaps.slice(0, 5),
    requires_human_approval: true,
  };

  await env.DB.prepare(
    "INSERT OR REPLACE INTO control_core_runs (run_date, core_version, status, decision_json, created_at) VALUES (?, ?, ?, ?, ?)"
  ).bind(decision.run_date, CONTROL_CORE_VERSION, decision.status, decisionJson, createdAt).run();

  await env.DB.prepare(
    "INSERT OR REPLACE INTO control_core_memory (memory_key, value_json, updated_at) VALUES (?, ?, ?)"
  ).bind("latest_control_decision", JSON.stringify(memory), createdAt).run();

  return { persisted: true, run_date: decision.run_date, memory_key: "latest_control_decision" };
}
