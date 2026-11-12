-- Separate AI control-core decision history and compact operational memory.
-- Store aggregate project state only; never visitor-level or credential data.
CREATE TABLE IF NOT EXISTS control_core_runs (
  run_date TEXT PRIMARY KEY,
  core_version TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('reviewed', 'needs_evidence')),
  decision_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS control_core_memory (
  memory_key TEXT PRIMARY KEY,
  value_json TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_control_core_runs_created
  ON control_core_runs (created_at DESC);
