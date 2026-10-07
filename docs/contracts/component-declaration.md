# Component declaration, format 1

| Contract control | Value                                                                          |
| ---------------- | ------------------------------------------------------------------------------ |
| Contract ID      | CORE-COMPONENT-1                                                               |
| Format           | `slow-thinker.component/1`                                                     |
| Schema           | [component-declaration-1.schema.json](schemas/component-declaration-1.schema.json) |
| Decisions        | [ADR 0020](../adr/0020-declared-component-configuration.md), [ADR 0016](../adr/0016-graph-document-model.md) |
| Journeys         | V01, V04, V05, V07                                                             |

Every component, whether provided by the platform or installed from a package,
has one declaration. A package ships it as `component.json` inside its importable
package, so that it is installed with the code. The platform reads it from the
installed environment and serves it in the catalog.
It describes how the component is placed in graphs, its ports, its state, the
platform services it uses, its configuration and how that configuration is shown.

## Fields

| Field            | Type             | Rule                                                                                         |
| ---------------- | ---------------- | -------------------------------------------------------------------------------------------- |
| `format`         | string           | Exactly `slow-thinker.component/1`                                                            |
| `type`           | string           | `^[a-z][a-z0-9-]{0,63}$`                                                                       |
| `version`        | string           | `major.minor.patch`                                                                           |
| `label`          | string           | 1–40 characters, shown in the palette and on cards                                            |
| `description`    | string           | 1–300 characters                                                                              |
| `icon`           | string           | One of `trigger`, `agent`, `router`, `output`, `memory`, `component`                            |
| `placements`     | array            | Non-empty subset of `node` (usable as a graph node), `output` (embeddable at a node's output) and `memory` (embeddable as a node's memory) |
| `state`          | string           | `stateless` or `stateful`                                                                     |
| `ports`          | object           | `inputs`: 0–16 port names. Either `outputs`: 0–32 port names, or `outputs_from`: a JSON Pointer into the configuration that holds the output names |
| `uses`           | array            | 0–8 service uses: `{"service": "llm", "pointer": "<JSON Pointer into config>"}`                |
| `config_schema`  | object           | JSON Schema, draft 2020-12, for the configuration object. Any `$schema` must name draft 2020-12; every `$ref` must be local and resolvable; every `pattern` must be a valid regular expression |
| `initial_config` | object           | Configuration of a newly added node; it may be incomplete and therefore invalid               |
| `ui`             | object           | Interface declaration, see below                                                              |

A component with placement `output` must declare `outputs_from`. Port names match
`^[a-z][a-z0-9_]{0,31}$` and are unique within their list.

### Service uses

A use names a platform service and the configuration location of its selection.
For the `llm` service the value at the pointer is either `null`, meaning nothing is
selected yet, or `{"llm": "<catalog entry id>", "parameters": {…}}`. The platform
validates that value against the [LLM catalog](llm-service.md); the component's
configuration schema should only require it to be an object or null. A declared
use is the component's authorization to call the selected entry and no other.

## Interface declaration

```json
{
  "card": ["/prompt", "/model"],
  "sections": [
    {"id": "prompt", "title": "Prompt", "fields": [
      {"path": "/prompt", "control": "multiline", "label": "Instructions",
       "help": "Sent to the model as system instructions."}
    ]}
  ]
}
```

| Field              | Rule                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------- |
| `card`             | 0–3 configuration pointers whose values appear on the canvas card                                 |
| `sections`         | 0–12 sections; `id` matches `^[a-z][a-z0-9_-]{0,31}$` and is unique; `title` has 1–40 characters  |
| `sections[].fields`| 1–24 fields                                                                                        |
| `path`             | JSON Pointer into the configuration, valid in `config_schema`                                     |
| `control`          | One of the controls below                                                                         |
| `label`            | 1–60 characters                                                                                    |
| `help`             | Optional, up to 300 characters                                                                     |
| `placeholder`      | Optional, up to 120 characters, for `text`, `multiline` and `code`                                 |
| `options`          | `choice` only: 1–32 `{"value": string, "label": string}`                                           |
| `language`         | `code` only: `python`, `json` or `text`                                                            |
| `service`          | `service` only: the service name, which must appear in `uses` with the same pointer               |
| `empty_label`      | `schema` only, optional: label of the `null` value, which means no format is required             |
| `item_label`       | `list` only, optional: label of one item, for example `Output`                                     |
| `when`             | Optional `{"path": pointer, "equals": string | number | boolean}`; the field is shown only when it holds |

Text is plain: no markup, scripts or remote resources are accepted anywhere. Patterns
follow ECMA-262 semantics: `$` matches only at the end of the string.

### Presentation

Fields and sections may carry presentation attributes; the platform renders every
component's form with the same design, so these refine layout without changing it.

| Attribute            | Applies to       | Values and default                                                                 |
| -------------------- | ---------------- | ---------------------------------------------------------------------------------- |
| `columns`            | section          | `1` (default) or `2`: fields flow in two columns; `full`-width fields span both     |
| `label_position`     | field            | `top` (default) or `start`: the label precedes the value on the same line          |
| `align`              | field            | `start`, `end` or `center`; default `end` for `number`, `start` otherwise          |
| `width`              | field            | `xs` (6rem), `sm` (10rem), `md` (20rem), `lg` (32rem) or `full`; default `sm` for `number`, `md` for `choice` and `list`, `lg` for `text`, `full` for the others |
| `format`             | `number` field   | `{"decimals": 0–6, "grouping": boolean, "prefix": string, "suffix": string}`, each optional; `prefix` and `suffix` have at most 8 characters, for example `$` or `tokens` |

Parameter forms that the platform generates from an LLM entry's parameter schema
follow the same defaults and use two columns.

### Controls

The platform renders exactly these controls. Constraints such as minimum, maximum
and length come from `config_schema` at the field's path.

| Control     | Value                                       | Rendering                                                                       |
| ----------- | ------------------------------------------- | ------------------------------------------------------------------------------- |
| `text`      | string                                      | Single-line input                                                               |
| `multiline` | string                                      | Expandable multi-line input                                                     |
| `number`    | integer or number                           | Numeric input honouring the schema's bounds                                     |
| `choice`    | one of the declared option values           | Select                                                                          |
| `list`      | array of strings                            | Ordered editable list with add and remove                                       |
| `code`      | string                                      | Monospaced editor with the declared language                                    |
| `schema`    | JSON Schema object, or `null` with `empty_label` | Schema editor with an option for “no format” when `empty_label` is present   |
| `service`   | service selection, see Service uses         | Entry selector followed by a form generated from the entry's parameter schema |

The generated parameter form supports `integer`, `number`, `string`, `boolean`,
`enum` with `title`, `default`, `minimum` and `maximum`, and disables properties
that an `if`/`else` branch sets to `false` for the current values.

### Summaries

The side panel shows one summary card per section, listing each field's value:
`multiline` and `text` as a preview of up to 120 characters, `choice` as the
option label, `list` joined by commas, `code` as its line count, `schema` as
`empty_label` or “JSON schema”, `service` as the entry label followed by its
parameter values, and a missing value as “Not set”. Cards on the canvas show the
values of `card` the same way.

### Node dialogs

A node's dialog shows the host component's sections, then each embedded
component's sections marked as embedded: the output component's, then the memory's. Apply validates the whole document;
Cancel discards the dialog's changes. Removing an embedded component lists the
connections that leave the ports it provided; confirming removes them.

## Platform components

| Component        | Placements | State     | Ports                     | Configuration                               |
| ---------------- | ---------- | --------- | ------------------------- | ------------------------------------------- |
| `trigger@1.0.0`  | `node`     | stateless | outputs `out`             | `message`: string, the run's default input  |
| `output@1.0.0`   | `node`     | stateless | inputs `in`               | None; the node name names the result        |

The trigger's `manual_runs` is `ask` (the default: a run started by hand asks for the
message, prefilled with `message`) or `send` (it sends `message` as it is).

Their declarations are part of the platform. Examples of all S06 declarations
are in [examples](examples/): [trigger](examples/trigger.component.json),
[output](examples/output.component.json), [LLM Call](examples/llm-call.component.json),
[Router](examples/router.component.json) and [Memory](examples/memory.component.json),
a package placed only as a node's memory: it adds the node's latest exchanges to each
new message, up to `max_exchanges` (1–100), for the run.
