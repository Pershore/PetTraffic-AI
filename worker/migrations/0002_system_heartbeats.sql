CREATE TABLE IF NOT EXISTS system_heartbeats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  checked_at TEXT NOT NULL,
  site_ok INTEGER NOT NULL CHECK (site_ok IN (0, 1)),
  site_status INTEGER NOT NULL,
  database_ok INTEGER NOT NULL CHECK (database_ok IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_system_heartbeats_checked_at
  ON system_heartbeats (checked_at DESC);
