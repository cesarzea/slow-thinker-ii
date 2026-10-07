# ui: specification

Presentation primitives and the generic configuration controls of the
[component declaration](../../../docs/contracts/component-declaration.md). No feature
imports; no network access.

## Public interface (`ui/index.ts`)

- Primitives, ported from `archive/s06-c11-wip` `frontend/src/ui/`: `Dialog`,
  `ConfigurationDialog`, `ConfigurationSummary`, `ExpandableTextArea` (value-based),
  `TextControl`, `ChoiceControl`, `ActionButton`, `Panel`, `moneyLabel`. Move their CSS
  from `app/styles/dialogs.css` and `features/workspace/workspace-dialogs.css` into `ui`.
- `ConfigurationField({field, schema, value, onChange, services, disabled})` renders one
  declared field by control: `text`, `multiline`, `number`, `choice`, `list`, `code`,
  `schema`, `service`. `value` and `onChange` carry plain JSON values; there is no
  patch or source-text model.
- `ParameterForm({schema, value, onChange})` renders a provider parameter schema:
  `integer`, `number`, `string`, `boolean`, `enum`, `title`, `default`, `minimum`,
  `maximum`, and disables properties that an `if`/`else` branch sets to `false` for the
  current values, with the note “Not available with the current settings.”
- `SchemaEditor({value, onChange, emptyLabel})` edits a JSON Schema for the `schema`
  control, adapted from `schema-definition/*` without any raw JSON escape.
- `summaryValue(field, value, services) -> string` implements the declaration's summary
  rules.
- Design system primitives on the tokens of `app/styles/base.css`: `Button` (variants
  `default`, `primary`, `accent`, `ghost`, `danger`; sizes `md`, `sm`; an optional
  leading icon), `IconButton` (named by its label, which is also its tooltip),
  `ButtonLink`, `Icon` (inline SVG line icons, `IconName`), `KindTile` (the coloured tile
  of a component kind, from its declared icon) and `MenuButton` (a short menu of
  actions with arrow keys and Escape; an optional text beside the trigger's icon, and
  items that are choices, `menuitemradio` with the chosen one ticked; items may carry a
  `group`, and consecutive items of a group sit under its small heading in a `group`
  named by it).
- `describeChange(before, after, catalog)` describes what a change did from its document
  and the one before it (“Moved Proposer”, “Connected Story · out → Proposer · in”, “and
  2 more”), for the History panel and the editor's Undo and Redo notices.
- Shared by the features: `NumberControl`, `Tabs`, `EvidenceContent`
  (recorded content as text or structure, never markup) and `useRead` (abortable reads,
  ported from `features/inspector`), JSON helpers (`readPointer`, `writePointer`,
  `schemaAt`, `isJsonObject`, `canonicalJson`), money helpers (`budgetShare`, `sumMoney`),
  text helpers (`textPreview`, `jsonPreview`, `fieldVisible`, `NOT_SET`) and run status
  text: `runStatusText(status, reason)` returns “Completed”, “Cancelled”, “Running”,
  “Starting”, or “Stopped: <reason label>” and “Failed: <reason label>” (“Stopped” or
  “Failed” alone without a reason); the run's detail is never part of it.
  `durationLabel` formats milliseconds as “250 ms” or “1.3 s”.

## Behaviour details

- `Dialog` is named by its title, keeps focus inside, closes on Escape and restores
  focus; handled keys do not reach an outer dialog, so dialogs can be nested.
  `ConfigurationDialog` keeps the names “Apply” and “Cancel” while applying; its
  `actions` are shown at the start of the footer. With `fixed`, a dialog has one size
  and place whatever it shows: `min(960px, 100vw - 2rem)` by `min(680px, 100dvh - 4rem)`,
  6vh from the top and centred; its content area scrolls and the footer stays in view.
- `Tabs` with `orientation="vertical"` form a list beside the panel and also move with
  the up and down arrows; consecutive items with the same `group` follow a heading with
  the group's name, which describes their tabs (it is not part of their names). The
  panel is replaced on every switch, so each section opens at its top.
- `ConfigurationSummary` is a row with a thin border: the title, an optional tag and a
  one-line `preview`, and a pencil “Edit <title>”. With `onToggle`, a click on the row
  shows or hides the values (the row is a button named by the title and described by
  the preview); collapsed values stay in the page, hidden.
- Every control shows its `help` under its label and reads it as its description.
  Fields carry the declaration's presentation with its defaults: `width` (`xs` 6rem,
  `sm` 10rem, `md` 20rem, `lg` 32rem, `full`; `sm` for numbers, `md` for choices and
  lists, `lg` for text, `full` otherwise), `align` (`end` for numbers), `label_position`
  and a section's `columns`; a number's `format` gives its decimals (the step), prefix
  and suffix, and formats its summary with grouping. Code has line numbers beside it.
- `ParameterForm` shows ordinary fields in two columns under the subheading
  “Parameters”, required ones first, each with its bounds (“1 to 384,000”) and any
  `description` as help. `SchemaEditor` edits properties as a table (Name, Type,
  Required, Minimum, Maximum, remove). `Dialog` and `ConfigurationDialog` take an `icon`
  before the title; `ConfigurationDialog` also takes a footer `note`.
- `ParameterForm` evaluates `if` conditions, including those inside `allOf`, with Ajv
  (draft 2020-12); a condition that cannot be compiled counts as satisfied. Values of
  properties that become unavailable are removed. Enumerations offer an unset option
  named “Default (<default>)” or “Not set”. A new service selection starts from the
  defaults the rules allow.
- `moneyLabel` shows `$` with at least two decimals and no trailing zeros beyond them.

## Acceptance

Unit tests cover each control, the parameter form's conditional disabling with the
DeepSeek schema, `when` visibility, summaries, keyboard focus in dialogs and the absence
of any raw JSON editor.

## Schema editor scope and accessible names

Step 1 edits object schemas with typed top-level properties, which covers the
validated journeys. Other valid schemas are preserved and shown read-only with the
note “This schema can be kept but not edited here.”

| Element                            | Role and name                                                                                                                                                                                                                 |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Format choice (with `empty_label`) | radio group named by the field label, options `empty_label` (for example “Any text”) and “JSON schema”                                                                                                                        |
| Add property                       | button “Add property”                                                                                                                                                                                                         |
| Property row                       | group “Property <n>” with textbox “Property name”, combobox “Type” (Text, Integer, Number, True or false, List of text), checkbox “Required”, spinbuttons “Minimum” and “Maximum” for numeric types, button “Remove property” |
| Generated schema                   | `{"type": "object", "additionalProperties": false, "properties": {…}, "required": […]}`                                                                                                                                       |
| Parameter form fields              | named by each property's `title`; disabled fields keep their name and show the note                                                                                                                                           |
| Service selector                   | combobox named by the field label, options named by entry labels                                                                                                                                                              |
| Properties table                   | each row a group “Property <n>”; the column headings are not read, as each input is named                                                                                                                                     |
| List control                       | textbox per item named “<item_label> <n>” by its visible label, buttons “Move <item_label> <n> up”, “Move <item_label> <n> down” (disabled at the ends), “Remove <item_label> <n>” (×) and “Add <item_label>”                 |
| Code control                       | textbox (multi-line) named by the field label, monospaced                                                                                                                                                                     |
| Choice control                     | combobox named by the field label                                                                                                                                                                                             |
| Multiline and text                 | textbox named by the field label                                                                                                                                                                                              |

Property rows without a name, or repeating a name, are kept in the editor but left out
of the generated schema. A list control without `item_label` names its items “Item <n>”.
The service selector starts with “Not selected”; a selected entry missing from the
catalog stays visible as “<id> (not available)”.
