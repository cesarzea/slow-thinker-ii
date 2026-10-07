-- Schema version 3 (ADR 0024): a graph has branches, `main` first. Changes and versions
-- belong to a branch; a version records the version it follows on its lineage (`parent`).
-- Change and version numbers stay unique per graph. Everything existing becomes branch
-- `main`, and each version follows the previous one. `folded` is the case-folded name,
-- unique per graph. Tables are rebuilt with foreign keys off; the migration checks them.

CREATE TABLE graph_branches (
  graph_id TEXT NOT NULL REFERENCES graphs (id),
  name TEXT NOT NULL,
  folded TEXT NOT NULL,
  created_at TEXT NOT NULL,
  from_version INTEGER,
  from_change INTEGER,
  PRIMARY KEY (graph_id, name),
  UNIQUE (graph_id, folded),
  FOREIGN KEY (graph_id, from_version) REFERENCES graph_versions (graph_id, version),
  FOREIGN KEY (graph_id, from_change) REFERENCES graph_changes (graph_id, change)
) STRICT;

INSERT INTO graph_branches (graph_id, name, folded, created_at, from_version, from_change)
SELECT id, 'main', 'main', created_at, NULL, NULL FROM graphs;

CREATE TABLE graph_changes_3 (
  graph_id TEXT NOT NULL REFERENCES graphs (id),
  change INTEGER NOT NULL CHECK (change >= 1),
  branch TEXT NOT NULL,
  at TEXT NOT NULL,
  name TEXT NOT NULL,
  document_json TEXT NOT NULL,
  PRIMARY KEY (graph_id, change),
  FOREIGN KEY (graph_id, branch) REFERENCES graph_branches (graph_id, name)
) STRICT;

INSERT INTO graph_changes_3 (graph_id, change, branch, at, name, document_json)
SELECT graph_id, change, 'main', at, name, document_json FROM graph_changes;

DROP TABLE graph_changes;

ALTER TABLE graph_changes_3 RENAME TO graph_changes;

CREATE INDEX graph_changes_by_branch ON graph_changes (graph_id, branch, change);

CREATE TABLE graph_versions_3 (
  graph_id TEXT NOT NULL REFERENCES graphs (id),
  version INTEGER NOT NULL CHECK (version >= 1),
  branch TEXT NOT NULL,
  parent INTEGER,
  change INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (graph_id, version),
  FOREIGN KEY (graph_id, branch) REFERENCES graph_branches (graph_id, name),
  FOREIGN KEY (graph_id, parent) REFERENCES graph_versions (graph_id, version),
  FOREIGN KEY (graph_id, change) REFERENCES graph_changes (graph_id, change)
) STRICT;

INSERT INTO graph_versions_3 (graph_id, version, branch, parent, change, created_at)
SELECT graph_id, version, 'main', CASE WHEN version > 1 THEN version - 1 END, change, created_at
FROM graph_versions;

DROP TABLE graph_versions;

ALTER TABLE graph_versions_3 RENAME TO graph_versions;

CREATE INDEX graph_versions_by_change ON graph_versions (graph_id, change);

CREATE INDEX graph_versions_by_branch ON graph_versions (graph_id, branch, version);
