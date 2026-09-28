CREATE TABLE managed_runs (
  run_id TEXT PRIMARY KEY,
  graph_revision TEXT NOT NULL,
  session_id TEXT NOT NULL,
  month_id TEXT NOT NULL,
  runtime_id TEXT NOT NULL,
  deadline REAL NOT NULL,
  snapshot_json TEXT NOT NULL CHECK (json_valid(snapshot_json)),
  state TEXT NOT NULL CHECK (state IN ('created','running','stopping','completed','failed','cancelled','timed_out','interrupted')),
  reason TEXT,
  event_sequence INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE managed_calls (
  call_id TEXT PRIMARY KEY,
  attempt_id TEXT NOT NULL UNIQUE,
  run_id TEXT NOT NULL REFERENCES managed_runs(run_id),
  parent_call_id TEXT REFERENCES managed_calls(call_id),
  context_json TEXT NOT NULL CHECK (json_valid(context_json)),
  request_json TEXT NOT NULL CHECK (json_valid(request_json)),
  charge_json TEXT CHECK (charge_json IS NULL OR json_valid(charge_json)),
  state TEXT NOT NULL CHECK (state IN ('reserved','dispatched','completed','failed','cancelled','interrupted'))
);
CREATE TABLE run_events (
  run_id TEXT NOT NULL REFERENCES managed_runs(run_id),
  sequence INTEGER NOT NULL,
  event TEXT NOT NULL,
  call_id TEXT,
  payload_json TEXT NOT NULL CHECK (json_valid(payload_json)),
  received_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  PRIMARY KEY(run_id, sequence)
);
