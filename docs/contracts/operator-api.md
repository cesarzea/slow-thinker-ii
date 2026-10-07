# Operator API, version 2

| Contract control | Value                                                                      |
| ---------------- | -------------------------------------------------------------------------- |
| Contract ID      | CORE-OPERATOR-API-2                                                        |
| Base path        | `/api/v2`                                                                  |
| Journeys         | J1–J3, V04, V10, V11                                                       |

The browser interface uses this API. Every request carries
`Authorization: Bearer <operator token>`; the token comes from the
`SLOW_THINKER_OPERATOR_TOKEN` environment variable. A server whose allowed hosts are
all loopback addresses may set `server.operator_authentication` to `none`; requests
then need no token. The server binds to loopback by default and always accepts only
its configured hosts and browser origins. Bodies are JSON.

`GET /access` needs no token and answers `{"authentication": "token" | "none"}`, so
the interface knows whether to ask for one.
Errors are `{"error": {"code": string, "message": string, "diagnostics"?: [...]}}`.

## Catalog

`GET /catalog` → `{"components": [declaration + {"origin": "platform" | "package"}],
"llms": [catalog entry]}`. Components follow the
[component declaration](component-declaration.md); LLM entries follow the
[LLM service](llm-service.md).

## Graphs

A graph has branches; the first is `main`. Each branch has a working copy whose every
edit is saved as a change; changes are never deleted, and restoring an earlier state
saves it as a new change. Activating a change creates the next immutable version on
that change's branch and makes it the graph's active version. A run executes either a
version or a change, activated or not: the editor's Run executes the branch's latest
change, what is on screen (see [ADR 0025](../adr/0025-runs-of-changes-and-run-mode.md)).
Activating an earlier version restores its document as a change and
activates that change. A branch starts from a version or a change of any branch;
there is no merge. Change and version numbers are unique per graph. See
[ADR 0024](../adr/0024-working-copy-and-activated-versions.md).

A draft document is a JSON object of at most 1 MiB with `format`
`slow-thinker.graph/1`, an `id` and a `name` valid under the
[graph document contract](graph-document.md); its other content may still have
diagnostics. Activation requires a document without error diagnostics. Documents are
compared and stored with their key order.

A branch name has 1–40 characters from letters, digits, space, `.`, `_` and `-`,
starts with a letter or digit, and is unique in the graph ignoring case.

| Request                                       | Result                                                                                         |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `POST /graphs/validate` `{"document"}`        | `200 {"diagnostics": [...]}`; never stores anything                                            |
| `GET /graphs`                                 | `200 {"graphs": [{"id", "name", "active_version", "latest_change", "updated_at"}]}`, most recently changed first; `active_version` is `null` before the first activation |
| `POST /graphs` `{"document"}`                 | `201 {"id", "branch": "main", "change": 1}` from a draft document; `409 graph_exists`; `422 invalid_document` with diagnostics |
| `GET /graphs/{id}/branches`                   | `200 {"branches": [{"name", "created_at", "from_version", "from_change", "latest_change", "head_version"}]}`, oldest first; `from_*` are `null` for `main`, `head_version` is the branch's latest version or `null` |
| `POST /graphs/{id}/branches` `{"name", "from": {"version"} or {"change"}}` | `201 {"name", "change"}`: the new branch's first change holds that document; `404 version_not_found` or `change_not_found`; `409 branch_exists`; `422 invalid_request` for a bad name |
| `POST /graphs/{id}/changes` `{"branch", "document"}` | `201 {"change", "at"}`; a document identical to the branch's latest change answers `200` with that change and adds nothing; `404 graph_not_found` or `branch_not_found`; `422 invalid_document`, including an `id` that differs from the path |
| `GET /graphs/{id}/changes?branch=&before=&limit=` | `200 {"changes": [{"change", "branch", "at", "name", "version"}]}`, newest first, at most 100 (default 50); without `branch`, every branch; `version` is the version activated from that change, or `null` |
| `GET /graphs/{id}/changes/{change}`           | `200 {"graph_id", "change", "branch", "at", "document", "version"}`; `404 change_not_found`     |
| `POST /graphs/{id}/versions` `{"change"}`     | `201 {"version", "branch", "change"}`: activates the change as the next version on its branch; `404 change_not_found`; `422 invalid_document` with the change's diagnostics |
| `GET /graphs/{id}`                            | `200 {"id", "name", "active_version", "latest_change", "branches": [...as above], "versions": [{"version", "branch", "parent", "change", "name", "created_at"}]}`; `parent` is the version this one follows on its lineage, or `null` |
| `GET /graphs/{id}/versions/{version}`         | `200 {"graph_id", "version", "branch", "parent", "change", "created_at", "document"}`; `404 version_not_found` |

## Runs

| Request                                                    | Result                                                                                  |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `POST /runs` `{"graph_id", "version" or "change", "input"}` | `202 {"run_id"}`; `404 graph_not_found`, `version_not_found` or `change_not_found`; `422 invalid_request` without exactly one of `version` and `change`; `422 invalid_document`; `409 too_many_runs` |
| `GET /runs?graph_id=&limit=`                               | `200 {"runs": [run summary]}`, newest first, at most 100                                |
| `GET /runs/{run_id}`                                       | `200` run summary plus `results`, `activations_by_node` and `messages_by_connection`    |
| `GET /runs/{run_id}/events?after=&limit=`                  | `200 {"events": [...], "last_seq", "finished"}`; at most 500 events per page            |
| `POST /runs/{run_id}/stop`                                 | `202 {"status"}`; stopping a finished run returns its final status                      |

A run summary is `{"run_id", "graph_id", "version", "change", "status", "reason",
"detail", "created_at", "ended_at", "totals"}`: `change` is the change the run executed
and `version` the version activated from it, or `null` for a change never activated. `results` lists `{"node_id", "name", "payload",
"at"}`. `messages_by_connection` maps `"<from> -> <to>"` to a count. Events follow
the [recording contract](recording.md). `input` is a JSON value; the interface sends
the edited Trigger message as a string.

## Usage

`GET /usage` → `{"day": {"key", "limit_usd", "used_usd"}, "month": {"key",
"limit_usd", "used_usd"}}`.
