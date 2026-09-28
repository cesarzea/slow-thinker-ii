CREATE TABLE operator_profiles (
  revision TEXT PRIMARY KEY,
  profile_json TEXT NOT NULL CHECK (json_valid(profile_json))
);
CREATE TABLE operator_workspace (
  singleton INTEGER PRIMARY KEY CHECK (singleton=1),
  profile_revision TEXT REFERENCES operator_profiles(revision),
  last_admitted_at REAL
);
INSERT INTO operator_workspace(singleton) VALUES(1);
CREATE TABLE operator_sessions (
  session_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  created_at REAL NOT NULL
);
CREATE TABLE operator_commands (
  command_id TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN ('session','start','stop')),
  request_json TEXT CHECK (request_json IS NULL OR json_valid(request_json)),
  receipt_json TEXT NOT NULL CHECK (json_valid(receipt_json))
);
CREATE TABLE operator_withdrawals (
  command_id TEXT PRIMARY KEY REFERENCES operator_commands(command_id),
  receipt_json TEXT NOT NULL CHECK (json_valid(receipt_json))
);
CREATE TABLE operator_runs (
  run_id TEXT PRIMARY KEY REFERENCES managed_runs(run_id),
  command_id TEXT NOT NULL UNIQUE REFERENCES operator_commands(command_id),
  profile_revision TEXT NOT NULL REFERENCES operator_profiles(revision),
  created_at REAL NOT NULL,
  cleanup_confirmed INTEGER NOT NULL DEFAULT 0 CHECK (cleanup_confirmed IN (0,1))
);
