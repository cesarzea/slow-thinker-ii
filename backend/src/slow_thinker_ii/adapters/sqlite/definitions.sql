CREATE TABLE personal_definitions (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    graph_id TEXT NOT NULL,
    revision TEXT NOT NULL,
    definition_json TEXT NOT NULL,
    parent_graph_id TEXT,
    parent_revision TEXT,
    parent_is_bundled INTEGER NOT NULL CHECK (parent_is_bundled IN (0, 1)),
    UNIQUE (graph_id, revision),
    CHECK ((parent_graph_id IS NULL AND parent_revision IS NULL AND parent_is_bundled = 0)
        OR (parent_graph_id IS NOT NULL AND parent_revision IS NOT NULL)),
    CHECK (parent_graph_id IS NULL OR parent_graph_id != graph_id OR parent_revision != revision)
);
CREATE INDEX personal_definitions_parent ON personal_definitions(parent_graph_id, parent_revision);
