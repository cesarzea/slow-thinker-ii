# Product configuration and execution workspace

> **S06-UX target update — 2026-10-02.**
> The S06-UX [interaction](workspace-interaction.md), [history/API](workspace-history-api.md),
> [presentation](component-presentation.md) and [frontend state](workspace-frontend-interfaces.md)
> contracts define the prepared correction target. They supersede conflicting
> presentation, per-field Apply and save-baseline requirements for that delivery;
> existing implemented APIs and runtime safeguards remain authoritative until their
> compatible additions are delivered.

The [S06 product completion specification](../specification/s06-product-completion.md)
adds the concrete screen, ordinary-form and readable-result requirements authorized
after owner review on 2026-10-02. The API contracts below remain authoritative.

| Document control | Value |
| --- | --- |
| Contract ID | CONTRACT-WORKSPACE-001 |
| Owner | Cesar Zea |
| Date | 2026-10-02 |
| Status | Active S06 delivery specification; implementation/verification pending |

## User journeys and navigation

Deliver coherent Experiments, Components, Resources, Runs and Settings navigation.
Keep the selected exact experiment/revision and any unsaved draft across navigation
within the authenticated workspace. Credentials remain memory-only; disconnect
clears protected draft/evidence state. Use a consistent responsive layout with
reusable forms, keyboard access and explicit loading, empty, pending, uncertain,
validation and error states. Authored content is English; runtime input is preserved.

Experiments supports creation from a chosen existing template, structured editing,
JSON import/edit, validation, immutable revisions/variants and execution. Forms
cover registered component types, names, prompts, supported model/reasoning options,
input/output schemas, internal workers/routers, optional resources, node input
bindings, authorized operations, sequence order, conditional routes and activation
limits. A generic schema-based configuration path preserves user-defined component
options; special LLM forms cannot replace that extension path.

Resources shows configured instances, their consumers, retention/sharing and exact
recorded activity. Components distinguishes reusable installed types from graph
instances. The canvas remains agent-centric under the approved visual model;
resource/controller inventories stay outside it. S06 uses forms for graph editing;
direct graphical authoring remains S14. Unsupported future graph profiles are not
presented as executable choices.

Runs supports session selection/creation, task input, Start/Stop, history and clear
results/cost summaries. Technical evidence is an optional panel/drawer with exact
run, activation and call identity; selecting it must make the content visible.
A saved run always displays its admitted graph and effective configuration. Keep
existing stale-view, unknown-command, cleanup and outstanding-cost semantics.
Settings exposes configured model profiles and editable effective deadlines/budgets
within trusted server ceilings, without exposing provider keys or endpoint fields.

## Discovery API

Authenticated `GET /api/v1/configuration/catalog` returns:

```json
{
  "schema_version": "1",
  "configuration_revision": "configured-revision",
  "components": [
    {
      "type_id": "llm-call",
      "type_version": "0.1.0-example",
      "roles": ["agent"],
      "config_schema": {},
      "resource_slots": {},
      "operations": {},
      "installation_status": "ready"
    }
  ],
  "models": [
    {
      "provider_profile": "deepseek-flash",
      "provider": "deepseek",
      "model": "deepseek-flash",
      "reasoning_efforts": ["none", "low", "high", "max"],
      "supports_temperature": true,
      "default_output_tokens": 1024,
      "maximum_output_tokens": 4096,
      "billing_profile": "deepseek.flash.direct.v1",
      "review_expires_at": 1791000000,
      "tariff_status": "ready"
    }
  ],
  "graph_schema": {},
  "schema_documents": {},
  "supported_graph_profiles": ["sequence", "bounded-conditional"],
  "limits": {"current": {}, "maximum": {}}
}
```

Schemas and operation dictionaries come from the exact trusted descriptors; empty
objects above illustrate shape only. `tariff_status` is `ready`, `unavailable`,
`stale` or `review_expired`, not an inferred promise that credentials will succeed.
An unavailable installed type remains visibly unavailable. Include every registered
external type, preserve opaque namespaced configuration, and never advertise a
hardcoded built-in-only component list. Reads neither install nor invoke components.
All API bodies/replies are bounded and use the existing operator authorization,
no-store policy and validated JSON/error boundaries. Viewer mode has no new writes.

## Structured source editing

`POST /api/v1/definitions/patch` takes unsaved source plus a bounded operations
list and returns canonical unsaved JSON text. It does not insert, execute, reserve
an identity or make a provider call. The operation uses JSON Pointer paths and
add/replace/remove semantics; values are JSON text to preserve large integers:

```json
{
  "source": "{...the complete current graph JSON...}",
  "operations": [
    {
      "op": "replace",
      "path": "/components/proposer/config/instructions",
      "value_json": "\"Produce a complete proposal.\""
    }
  ]
}
```

`add`/`replace` require `value_json`; `remove` forbids it. Reject malformed source,
invalid JSON values, unknown operation fields, malformed/missing pointers and
excessive operation counts/body sizes. Apply all operations to an isolated decoded
source and return nothing partially modified on failure. Preserve unrelated
fields/extensions and Python numeric values under the existing S03 canonical
semantics, including integers above JavaScript's safe integer range and `1.0`.
Allow incomplete structural drafts; full definition validation and installed runtime
preflight remain separate existing gates before Save and Start.

Frontend form edits call this endpoint rather than parse/stringify the entire
source. Match replies to the submitted source and discard obsolete edits. Pending
patch/derive/save work locks conflicting actions. Generic JSON/schema field values
also travel as `value_json`, not a browser-rounded reconstruction. Form and JSON
modes share one dirty baseline, validation result and exact-source uncertain-save
recovery. Bindings do not implicitly grant permissions: present authorized operations
explicitly and update permissions only through an intentional configuration action.

## Bounded configuration commands

`POST /api/v1/configuration/limits` takes `command_id` (32 lowercase hex digits),
`expected_revision` and a nonempty `limits` object. Supported fields are positive
`run_seconds`, `call_seconds`, `startup_seconds`, `shutdown_seconds`, `max_calls`,
`max_depth`, `max_payload_bytes` and nonnegative USD decimal strings `run_budget`,
`session_budget`, `month_budget`. Reject unknown fields, nonfinite values, excess
precision, call > run duration and values above trusted startup ceilings. Values
not supplied retain the current effective settings. Do not increase the USD 3
allowance or reset settled/reserved spending.

Success returns `{command_id, configuration_revision, replayed}`. Configuration
revisions are immutable; keep the graph's trusted limits-policy identifier and
freeze changed effective values under the new configuration revision. A request
with an old expected revision fails as a conflict. Existing active execution
prevents a change; a queued old-revision start must fail existing revision checks.
Reject caps below existing session/month commitments. Save the request digest,
new configuration and result atomically, then make the new revision current.
Replay of the same command/body returns its original result; a changed body with
the same ID conflicts. An uncertain response must retain the exact submitted body
for safe replay. No business/provider calls occur in configuration.

The application `workspace` namespace owns source patching and configuration use
cases with injected public ports; framework/database details remain in adapters.
SQLite migration adds scoped tariff records and configuration command receipts,
retaining the existing verified backup and transactional migration behavior.
Bootstrap supplies the discovery source, ceiling profile and component/resource
adapters. New routes compose these services through their public entry points.

Acceptance and ownership are in [the delivery block](../specification/s04-s06-delivery.md).

## Exact limit projection and errors

Both limits.current and limits.maximum contain the eleven supported fields.
Durations are finite positive JSON numbers (fractional seconds are allowed);
counts are positive JSON integers; budgets are exact USD decimal strings.
Neither projection contains a policy/configuration revision. A successful patch
returns an object even when an incomplete draft lacks graph identity.

Errors retain the existing schema_version 0.1-draft envelope and error fields
code, message and request_id. Fixed new mappings are: invalid_patch (422),
invalid_limits (422), configuration_conflict (409: stale revision or changed body
under the same command ID), configuration_active (409) and
budget_below_commitments (422). Malformed JSON remains invalid_json (400); existing
transport/authentication codes remain; unexpected storage/discovery failure is
operator_service_unavailable (503). Exception text is not exposed.

Discovery also supplies schema_documents, a dictionary keyed by each trusted local
schema URN. Component schemas remain exact; forms resolve their $ref/allOf through
this dictionary and local fragments only, without network schema resolution.
Unknown schema constructs retain explicit JSON value editing. JSON Pointer root
add/replace accepts an object; removing the object root is invalid.
