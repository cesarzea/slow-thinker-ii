CREATE TABLE IF NOT EXISTS budget_scopes (
  kind TEXT NOT NULL CHECK (kind IN ('run', 'session', 'month')),
  scope_id TEXT NOT NULL,
  cap INTEGER NOT NULL CHECK (typeof(cap) = 'integer' AND cap >= 0),
  settled INTEGER NOT NULL DEFAULT 0 CHECK (typeof(settled) = 'integer' AND settled >= 0),
  reserved INTEGER NOT NULL DEFAULT 0 CHECK (typeof(reserved) = 'integer' AND reserved >= 0),
  PRIMARY KEY (kind, scope_id)
);
CREATE TABLE IF NOT EXISTS spending_attempts (
  attempt_id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  month_id TEXT NOT NULL,
  bound INTEGER NOT NULL CHECK (bound >= 0),
  state TEXT NOT NULL CHECK (state IN ('reserved', 'dispatched', 'settled', 'released')),
  amount INTEGER,
  source TEXT
);
CREATE TABLE IF NOT EXISTS spending_evidence (
  sequence INTEGER PRIMARY KEY AUTOINCREMENT,
  attempt_id TEXT NOT NULL REFERENCES spending_attempts(attempt_id),
  event TEXT NOT NULL,
  amount INTEGER,
  source TEXT,
  received_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE TABLE IF NOT EXISTS tariff_revisions (
  digest TEXT PRIMARY KEY,
  retrieved_at INTEGER NOT NULL,
  source TEXT NOT NULL,
  tariff_json TEXT NOT NULL,
  source_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tariff_refresh (
  sequence INTEGER PRIMARY KEY AUTOINCREMENT,
  attempted_at INTEGER NOT NULL,
  digest TEXT REFERENCES tariff_revisions(digest),
  error TEXT,
  CHECK ((digest IS NULL) != (error IS NULL))
);
