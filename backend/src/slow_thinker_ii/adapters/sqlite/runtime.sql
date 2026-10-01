CREATE TABLE pricing_quarantine (
  tariff_revision TEXT PRIMARY KEY,
  pricing_json TEXT NOT NULL CHECK (json_valid(pricing_json)),
  call_id TEXT NOT NULL REFERENCES managed_calls(call_id),
  bound INTEGER NOT NULL,
  amount INTEGER NOT NULL,
  recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE process_ownership (
  marker TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES managed_runs(run_id),
  runtime_id TEXT NOT NULL,
  instance_id TEXT NOT NULL,
  workspace TEXT NOT NULL,
  identity_json TEXT CHECK (identity_json IS NULL OR json_valid(identity_json)),
  state TEXT NOT NULL CHECK(state IN ('launching','running','stopped','unconfirmed')),
  reason TEXT,
  UNIQUE(run_id,instance_id)
);
