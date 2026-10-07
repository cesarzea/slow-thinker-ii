-- Schema version 2 (ADR 0024): each graph's working copy is an append-only history of numbered
-- changes, and versions are activated from changes. Each version 1 graph version becomes the
-- change of the same number, document and time, linked to it. The graph name and every graph
-- summary value come from the changes and versions; `graphs` keeps identity and creation only.
-- Tables are rebuilt with foreign keys off; the migration checks them before it commits.

CREATE TABLE graph_changes (
  graph_id TEXT NOT NULL REFERENCES graphs (id),
  change INTEGER NOT NULL CHECK (change >= 1),
  at TEXT NOT NULL,
  name TEXT NOT NULL,
  document_json TEXT NOT NULL,
  PRIMARY KEY (graph_id, change)
) STRICT;

INSERT INTO graph_changes (graph_id, change, at, name, document_json)
SELECT graph_id, version, created_at, name, document_json FROM graph_versions;

CREATE TABLE graph_versions_2 (
  graph_id TEXT NOT NULL REFERENCES graphs (id),
  version INTEGER NOT NULL CHECK (version >= 1),
  change INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (graph_id, version),
  FOREIGN KEY (graph_id, change) REFERENCES graph_changes (graph_id, change)
) STRICT;

INSERT INTO graph_versions_2 (graph_id, version, change, created_at)
SELECT graph_id, version, version, created_at FROM graph_versions;

DROP TABLE graph_versions;

ALTER TABLE graph_versions_2 RENAME TO graph_versions;

CREATE INDEX graph_versions_by_change ON graph_versions (graph_id, change);

CREATE TABLE graphs_2 (
  id TEXT PRIMARY KEY NOT NULL,
  created_at TEXT NOT NULL
) STRICT;

INSERT INTO graphs_2 (id, created_at) SELECT id, created_at FROM graphs;

DROP TABLE graphs;

ALTER TABLE graphs_2 RENAME TO graphs;
