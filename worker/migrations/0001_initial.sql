CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN (
    'analytics_snapshot',
    'topic_snapshot',
    'control_center_snapshot',
    'recommendation_snapshot'
  )),
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_kind_created
  ON events (kind, created_at DESC);

CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  task_type TEXT NOT NULL CHECK (task_type IN (
    'collect_analytics',
    'scan_topics',
    'check_site',
    'audit_technical_seo',
    'review_content_facts'
  )),
  assigned_agent TEXT NOT NULL CHECK (assigned_agent IN (
    'coordinator',
    'analytics',
    'topics',
    'technical-seo',
    'content-review'
  )),
  priority INTEGER NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
  payload_json TEXT NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed')),
  claimed_by TEXT,
  claimed_at TEXT,
  attempt_count INTEGER NOT NULL DEFAULT 0,
  result_json TEXT,
  created_at TEXT NOT NULL,
  completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_claim
  ON tasks (status, assigned_agent, priority DESC, created_at ASC);
