CREATE TABLE IF NOT EXISTS agent_runs (
 run_date TEXT PRIMARY KEY,
 status TEXT NOT NULL CHECK (status IN ('running','completed','failed')),
 ai_calls INTEGER NOT NULL DEFAULT 0 CHECK (ai_calls BETWEEN 0 AND 5),
 report_json TEXT,
 error_code TEXT,
 started_at TEXT NOT NULL,
 completed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_agent_runs_status_started ON agent_runs(status,started_at DESC);
