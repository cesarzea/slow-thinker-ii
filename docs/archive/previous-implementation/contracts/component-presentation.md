# Declarative component presentation

**S06-UX-PRESENTATION / revision 2 / 2026-10-02.** Owner-authorized implementation; locally verified. Extends [component discovery](product-workspace.md#discovery-api) without
changing operation, resource-slot, permission or component execution semantics.

## Metadata ownership and precedence

Component authors may provide `extensions["slow-thinker:ui"]` in a versioned
descriptor. Do not modify already installed descriptor bytes or reuse a version
with changed meaning. Discovery returns a normalized optional `presentation` object
and `presentation_status: "declared" | "compatibility" | "generic" | "invalid"`.
Discovery also returns `presentation_warning: string | null`, a safe explanation
bounded to 500 characters when normalization fails. Otherwise it is null. Older
responses may omit these additive fields and retain generic presentation.

For existing bundled types only, the workspace adapter owns trusted compatibility
profiles keyed by exact `(type_id, type_version)`. This avoids modifying historical
descriptors/installation hashes merely to add presentation. Profiles live inside
`adapters/workspace/presentation/`; they contain data, not arbitrary UI code. No
prefix, subclass-name or property-name inference applies to unknown versions.

Valid descriptor metadata takes precedence. Absent metadata may use an exact
compatibility profile. Invalid or unsupported-version metadata yields generic forms
and a visible metadata warning; it does not silently apply a profile with possibly
different semantics. Discovery never installs a component or grants authority.

## Version 1 profile

```json
{
  "version": 1,
  "display_name": "LLMCall",
  "icon": "ai-agent",
  "primary_child_slot": null,
  "instructions_pointer": "/instructions",
  "model_slot": "model",
  "provider_profile_pointer": null,
  "model_pointer": null,
  "generation": {
    "reasoning_pointer": "/parameters/reasoning_effort",
    "temperature_pointer": "/parameters/temperature",
    "output_tokens_pointer": "/parameters/max_completion_tokens"
  },
  "response": {"format_pointer": "/output/format", "schema_pointer": "/output/schema"},
  "slots": {"model": {"label": "Model", "placement": "resource"}}
}
```

All fields except version are optional and nullable; null means unavailable,
including display_name, icon, generation, response and slots. Optional nested slot
label/placement normalize to null. Non-null values still require the declared shape.
Pointers
are relative to this instance's config, not the entire graph. `icon` is one of
ai-agent, component, tool, memory or model; unknown values make metadata invalid.
Names and slot labels are plain text, at most 160 characters. No HTML, executable
renderers, expressions or remote schema URLs are accepted. Reject unknown profile
fields and dangling slot names. Each pointer must resolve through the config schema (local refs/compositions
permitted), including keys allowed by additionalProperties. For example, LLMCall's
parameters object permits native option keys without declaring each property.
Reject paths forbidden by a closed object schema; optional instance values may
be absent. Missing generation/response groups omit specialized controls.

`primary_child_slot` names a resource slot used for a component's main worker.
Follow actual bindings at most 16 levels with a visited-instance set. Editing always
identifies the resolved child; missing bindings and cycles show a problem instead
of choosing another component. `model_slot` names the bound model instance whose
profile has a provider_profile_pointer. Neither implies a provider call occurred.
An optional `model_pointer` identifies the model-name field in that bound instance.
When declared, selecting a configured provider profile updates both pointers in
one patch. This avoids inferring fields from type or property names. The exact
model-provider 0.1.0 compatibility profile declares `/model` alongside
`/provider_profile`; both are required by its existing config schema.

Slot placement is `component` or `resource`; it governs available create/contain
versus connect actions. The existing slot role and required operations determine
compatibility, not the display label. Actual `contained_by` and resource references
determine existing placement, even if metadata suggests another default. Metadata
cannot make an incompatible existing binding valid or change its containment.
Unknown slots remain accessible through a generic binding control without invented
containment. Slot cardinality stays one target per existing slot contract; arbitrary
multiple children require explicit slots or a future contract, not an extra array.

## Built-in compatibility and fallback

Create profiles for exact registered versions of LLMCall, RoutedCall,
ContextualCall, model-provider, calculator, key-value-memory and Redirector that are
present in the installed catalog. Resolve their field paths against the canonical
schemas, not observed example values. LLMCall uses the paths in the example above;
RoutedCall/ContextualCall identify their declared worker slot; model-provider uses
`/provider_profile`. Other types use schema titles/descriptions and explicit slots.
Keep unsupported controller editing with the existing execution-profile forms.

Generic component forms cover schema-supported scalars, objects, arrays and enums;
unknown constructs offer Advanced JSON preserving source values. The catalog, not
a list in the browser, determines available types and exact versions. Optional
metadata enhances these forms but is not required for a component to be usable.

Model capability limits come from catalog.models matched by the bound model's
provider profile. Preserve native parameter values as exact source. A profile or
reasoning change lists incompatible parameters and requires confirmation of their
removal/reset in the same patch. Do not clear unknown parameters speculatively.
Context/memory use remains controlled by agent implementation, not UI attachment.

Discovery supplies normalized metadata; the frontend validates it again. Historical
run configuration uses admitted descriptors/configuration and exact-version profiles,
never a current descriptor of another version. Unavailable metadata uses generic
presentation without changing the meaning of retained evidence.

## Delivery checkpoint — 2026-10-03

The owner-authorized S06 implementation and unchanged mandatory verification are
complete. The [current sprint report](../progress/sprint-06-status-report.md)
records acceptance evidence and preserved compatibility. Contract revision numbers
and runtime/accounting requirements are unchanged; owner usability review is separate.

## Historical model presentation correction — 2026-10-03

The S06 fidelity correction adds the exact compatibility identity
`example.model-resource@0.1.0-example`, declaring provider profile `/provider_profile`
and model `/model` from its unchanged closed schema. This restores the ordinary
model selector in existing examples without changing descriptor bytes, hashes,
provider requests or generic fallback for unknown versions. Verification of this
correction remains pending; prior technical evidence is not owner acceptance.

## Component-owned dialog correction — 2026-10-03

The [version-2 dialog contract](component-dialogs.md) supersedes the platform-owned
compatibility-profile location and ordinary editing rules above for the reopened
S06 scope. Exact historical identities may carry presentation records within their
component package; discovery consumes them through trusted generic metadata roots.
Historical runtime descriptor bytes and hashes remain unchanged. Version-1 records
remain supported. Prior checkpoint statements retain their historical tested scope;
the [composition correction](../specification/s06-composition-and-dialogs.md) is in
development and requires new verification.
