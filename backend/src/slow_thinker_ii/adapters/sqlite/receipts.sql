CREATE TABLE call_receipts (
  receipt_id TEXT PRIMARY KEY,
  call_id TEXT NOT NULL REFERENCES managed_calls(call_id),
  receipt_json TEXT NOT NULL CHECK (json_valid(receipt_json)),
  outcome_json TEXT NOT NULL CHECK (json_valid(outcome_json)),
  received_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
ALTER TABLE managed_calls ADD COLUMN result_receipt_id TEXT REFERENCES call_receipts(receipt_id);
ALTER TABLE managed_calls ADD COLUMN reason TEXT;
CREATE INDEX run_events_by_call ON run_events(call_id, event);
