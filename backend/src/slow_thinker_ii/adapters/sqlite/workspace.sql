CREATE TABLE model_tariff_revisions (
  profile_id TEXT NOT NULL,
  digest TEXT NOT NULL,
  retrieved_at INTEGER NOT NULL,
  source TEXT NOT NULL,
  tariff_json TEXT NOT NULL CHECK(json_valid(tariff_json)),
  source_json TEXT NOT NULL CHECK(json_valid(source_json)),
  PRIMARY KEY(profile_id,digest)
);
CREATE TABLE model_tariff_refresh (
  sequence INTEGER PRIMARY KEY,
  profile_id TEXT NOT NULL,
  attempted_at INTEGER NOT NULL,
  digest TEXT,
  error TEXT,
  CHECK((digest IS NULL) != (error IS NULL)),
  FOREIGN KEY(profile_id,digest) REFERENCES model_tariff_revisions(profile_id,digest)
);
CREATE INDEX model_tariff_attempts ON model_tariff_refresh(profile_id,sequence);
CREATE TABLE configuration_commands (
  command_id TEXT PRIMARY KEY,
  request_json TEXT NOT NULL CHECK(json_valid(request_json)),
  configuration_revision TEXT NOT NULL REFERENCES operator_profiles(revision)
);
