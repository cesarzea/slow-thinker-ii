# Component-owned configuration dialogs

**S06-DIALOGS / 1 — 2026-10-03.** Owner-authorized S06 contract. Extends
[presentation version 1](component-presentation.md), preserving its optional fields
and historical normalization. Runtime semantics and authority are separate.

## Ownership, transport and versioning

Descriptors may declare extensions["slow-thinker:ui"] version 2. Bundled historical
descriptors may use package-owned presentation.json records with exact type_id and
type_version, profile version and profile digest. Discovery loads those records
through an injected trusted metadata directory, never a platform type-name map.
Preparation/bundling distributes the component's record with its descriptor.
Each package-owned presentation.json is {type_id:string,type_version:string,
presentation:<versioned profile>,attachment?:<versioned attachment>}; one record
per identity, or a bounded records array in the same file for a package implementing
multiple historical identities. A copies exact package records into trusted catalog
metadata roots; conflicting identities fail visibly. Profile hashes are discovery
provenance, not replacements for runtime installation hashes.
Inline declared metadata takes precedence; invalid metadata is visible and falls
back generically. Historical descriptor bytes/installations remain unchanged.
External descriptors may inline the same data without registering platform code.

Package metadata is selected from the immutable installation resolution selected
for that exact component identity. The installation catalog returns only recorded,
size-bounded presentation paths whose bytes match their recorded SHA-256 digest;
metadata lookup does not execute a component or inspect its environment. A
dependency record cannot override another component's own selected resolution.
Discovery never scans all retained installations or selects records by recency.
Repository metadata is a compatibility fallback only when the selected resolution
contains no matching record. Missing, altered or conflicting selected records fail
visibly rather than silently falling back to newer source metadata.

Version 2 retains version-1 identity/primary-child/model/generation/response/slot
fields and adds dialogs and summaries. No executable renderer, HTML, remote URL,
unbounded recursion or expression evaluation is allowed. A future control version
can extend the public vocabulary without embedding a specific component in the app.

```json
{
  "version": 2,
  "display_name": "LLMCall",
  "icon": "ai-agent",
  "instructions_pointer": "/instructions",
  "model_slot": "model",
  "dialogs": [
    {
      "id": "prompt",
      "title": "Prompt",
      "description": "Instructions supplied to the model.",
      "fields": [
        {"label":"Prompt","pointer":"/instructions","control":"multiline"}
      ],
      "summary": [
        {"label":"Prompt","pointer":"/instructions","format":"preview"}
      ]
    }
  ]
}
```

## Exact normalized frontend boundary

ComponentPresentation.version is 1 | 2; dialogs is optional readonly
ComponentDialog[] | null. All old fields retain their types. ComponentDialog:
id/title required strings, description optional string, fields readonly
ComponentDialogField[], summary optional readonly ComponentSummaryField[].

ComponentDialogField has required label and control; optional pointer, slot,
options, when and description. control is one of value, multiline, schema, model,
reasoning, temperature, output-tokens, native-parameters, response-format,
connections, permissions. pointer is relative to config; slot names an actual
declared binding. options is readonly {value:string,label:string}[] and may restrict
ordinary choices without changing runtime validation. when is optional
{pointer:string,equals?:scalar,exists?:boolean}; both conditions, if supplied, apply.
ComponentSummaryField: label required; pointer optional; format is text, preview,
count, model or binding; slot optional. Cap fields/dialogs/summary count and labels,
validate pointer and slot declarations, reject unknown controls and duplicate IDs.
Default ordinary value controls come from the component config schema. Component
authors choose grouping/titles/descriptions; the platform supplies reusable widgets.

UI public exports ConfigurationDialog and ConfigurationSummary plus these types.
ComponentPresentation may also declare `supported_providers`, an optional nullable
array of one to sixteen unique provider IDs matching `[a-z][a-z0-9_-]{0,63}`.
This is component-owned compatibility metadata, not a platform type-name rule.
The Model control filters current reviewed profiles using the actual bound model
resource's declaration. An incompatible current selection remains visible with a
repair explanation; it is never silently replaced. Final candidate validation and
save compare the declared provider-profile pointer with the current workspace
profile's provider. Missing/null declarations preserve generic historical behavior;
retained immutable metadata is not rewritten to introduce a new restriction.

ConfigurationDialogProps: title:string; description?:string; pending?:boolean;
error?:string|null; onApply:()=>void|Promise<void>; onCancel:()=>void;
children:ReactNode. It uses the existing accessible Dialog, one modal only and
explicit Apply/Cancel footer. Workspace owns isolated source/field buffers and
passes controls. UI does not import workspace. ConfigurationSummaryProps:
title:string; description?:string; values:readonly {label:string,value:string}[];
onEdit:()=>void; disabled?:boolean. It renders read-only values and Edit.

## Behavior and completeness

Inspector summaries are selected from actual configured instances, following the
declared primary child. Internal component edits identify the full breadcrumb.
Apply stages exactly one coherent patch against the latest unchanged source;
Cancel/Close/Escape discard local dialog changes. Save revision is distinct.
The optional workspace public callback `validateDraft(source:string):Promise<void>`
is supplied by the authenticated app through the existing exact-source definition
validation endpoint. Ordinary Apply requires a fully validated final candidate and
rechecks source staleness after asynchronous work; missing/unavailable validation
retains local changes with an actionable error. Expert graph source may remain
incomplete. Failed validation does not modify the shared draft.

No stacked dialogs: changing a concept replaces the content of one modal or closes
it before opening the next. Explicitly block navigation while a structural command
is committing, and retain actionable errors in its dialog.

Every bundled component supplies version-2 groups for all ordinary configuration.
Full supported JSON Schema structures need recursive fields for object/array/types,
enum/const, required/additional properties, references, oneOf/anyOf/allOf and
if/then/else conditions. Unknown authored keywords remain preserved and editable
as explicit additional fields; expert JSON remains optional. Native generation
parameters use a named-entry editor, retaining unknown native fields exactly.
External types without dialogs receive a generic Configuration dialog with typed
fields and optional expert source, never an unusable disabled inspector.
