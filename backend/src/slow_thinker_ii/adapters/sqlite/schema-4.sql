-- Schema version 4: a run executes a change, activated or not. `graph_change` is the change
-- it executed; `graph_version` the version that change became, or NULL for a run of a change
-- that was never activated. Existing runs keep their version and gain its change.

CREATE TABLE runs_4 (
  id TEXT PRIMARY KEY NOT NULL,
  graph_id TEXT NOT NULL,
  graph_version INTEGER,
  graph_change INTEGER NOT NULL,
  status TEXT NOT NULL,
  reason TEXT,
  detail TEXT NOT NULL,
  input_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  ended_at TEXT,
  totals_json TEXT,
  FOREIGN KEY (graph_id, graph_version) REFERENCES graph_versions (graph_id, version),
  FOREIGN KEY (graph_id, graph_change) REFERENCES graph_changes (graph_id, change)
) STRICT;

INSERT INTO runs_4 (id, graph_id, graph_version, graph_change, status, reason, detail,
  input_json, created_at, ended_at, totals_json)
SELECT r.id, r.graph_id, r.graph_version, v.change, r.status, r.reason, r.detail,
  r.input_json, r.created_at, r.ended_at, r.totals_json
FROM runs r JOIN graph_versions v ON v.graph_id = r.graph_id AND v.version = r.graph_version
ORDER BY r.rowid;

DROP TABLE runs;

ALTER TABLE runs_4 RENAME TO runs;

CREATE INDEX runs_by_graph ON runs (graph_id, created_at);
