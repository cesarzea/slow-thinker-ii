-- Schema version 1: graphs and their versions, runs and their events, the budget ledger.
-- Times are UTC text, "YYYY-MM-DDTHH:MM:SS.ffffffZ"; amounts are integer quanta of 1e-9 USD.

CREATE TABLE graphs (
  id TEXT PRIMARY KEY NOT NULL,
  name TEXT NOT NULL,
  latest_version INTEGER NOT NULL CHECK (latest_version >= 1),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
) STRICT;

CREATE TABLE graph_versions (
  graph_id TEXT NOT NULL REFERENCES graphs (id),
  version INTEGER NOT NULL CHECK (version >= 1),
  name TEXT NOT NULL,
  document_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (graph_id, version)
) STRICT;

CREATE TABLE runs (
  id TEXT PRIMARY KEY NOT NULL,
  graph_id TEXT NOT NULL,
  graph_version INTEGER NOT NULL,
  status TEXT NOT NULL,
  reason TEXT,
  detail TEXT NOT NULL,
  input_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  ended_at TEXT,
  totals_json TEXT,
  FOREIGN KEY (graph_id, graph_version) REFERENCES graph_versions (graph_id, version)
) STRICT;

CREATE INDEX runs_by_graph ON runs (graph_id, created_at);

CREATE TABLE run_events (
  run_id TEXT NOT NULL REFERENCES runs (id),
  seq INTEGER NOT NULL CHECK (seq >= 1),
  at TEXT NOT NULL,
  elapsed_ms INTEGER NOT NULL CHECK (elapsed_ms >= 0),
  kind TEXT NOT NULL,
  evidence TEXT NOT NULL CHECK (evidence IN ('observed', 'reported')),
  node_id TEXT,
  activation_id TEXT,
  data_json TEXT NOT NULL,
  PRIMARY KEY (run_id, seq)
) STRICT;

CREATE TABLE ledger (
  call_id TEXT PRIMARY KEY NOT NULL,
  run_id TEXT NOT NULL,
  day_key TEXT NOT NULL,
  month_key TEXT NOT NULL,
  reserved INTEGER NOT NULL CHECK (reserved >= 0),
  charge INTEGER CHECK (charge >= 0),
  estimated INTEGER NOT NULL CHECK (estimated IN (0, 1)),
  reserved_at TEXT NOT NULL,
  settled_at TEXT
) STRICT;

CREATE INDEX ledger_by_run ON ledger (run_id);
CREATE INDEX ledger_by_day ON ledger (day_key);
CREATE INDEX ledger_by_month ON ledger (month_key);
