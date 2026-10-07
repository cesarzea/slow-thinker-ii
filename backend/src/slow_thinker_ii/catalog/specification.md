# catalog: specification

Implements the [component declaration](../../../../docs/contracts/component-declaration.md)
and the catalog side of the [LLM service](../../../../docs/contracts/llm-service.md).
Pure domain code: no I/O except reading its own package data.

## Public interface (`slow_thinker_ii.catalog`)

```python
@dataclass(frozen=True)
class ComponentRef:
    type: str
    version: str
    @staticmethod
    def parse(text: str) -> "ComponentRef"        # "llm-call@1.0.0"; ValueError if malformed
    def __str__(self) -> str                       # "llm-call@1.0.0"

@dataclass(frozen=True)
class ServiceUse:
    service: str                                   # "llm"
    pointer: str                                   # JSON Pointer into the configuration

@dataclass(frozen=True)
class ComponentDeclaration:
    ref: ComponentRef
    label: str
    placements: frozenset[str]                     # subset of {"node", "output"}
    stateful: bool
    inputs: tuple[str, ...]
    outputs: tuple[str, ...] | None                # None when outputs_from is declared
    outputs_from: str | None
    uses: tuple[ServiceUse, ...]
    config_schema: JsonObject
    initial_config: JsonObject
    document: JsonObject                           # the validated declaration, served as is
    def output_ports(self, config: JsonObject) -> tuple[str, ...]

class DeclarationError(ValueError):
    issues: tuple[str, ...]                        # English, each naming the offending field

def parse_declaration(document: JsonValue) -> ComponentDeclaration
def platform_declarations() -> tuple[ComponentDeclaration, ...]   # trigger@1.0.0, output@1.0.0
TRIGGER: ComponentRef                              # trigger@1.0.0
OUTPUT: ComponentRef                               # output@1.0.0

@dataclass(frozen=True)
class LlmModelSettings:
    id: str; label: str; provider: str; model: str
    max_output_tokens: int; default_output_tokens: int
    reasoning_efforts: tuple[str, ...]
    temperature: Literal["unsupported", "supported", "without_reasoning"]

@dataclass(frozen=True)
class LlmEntry:
    id: str; label: str; provider: str
    parameters: JsonObject                         # generated JSON Schema
    def document(self) -> JsonObject               # {"id", "label", "provider", "parameters"}
    def parameter_problems(self, parameters: JsonObject) -> tuple[str, ...]   # sorted; () when valid
    def with_defaults(self, parameters: JsonObject) -> JsonObject             # a copy

def llm_entry(settings: LlmModelSettings) -> LlmEntry

@dataclass(frozen=True)
class SchemaProblem:
    path: tuple[str, ...]          # JSON Pointer tokens of the offending value; missing members included
    keyword: str                   # the failing keyword; "" for a `false` schema
    phrase: str                    # "must be at most 128000"
    sentence: str                  # "Max output tokens must be at most 128000."
    @staticmethod
    def label_of(path: tuple[str, ...], labels: Sequence[tuple[tuple[str, ...], str]] = (),
                 fallback: str = "Value") -> str

def schema_problems(schema: JsonObject, value: JsonValue,
                    labels: Sequence[tuple[tuple[str, ...], str]] | None = None,
                    fallback: str = "Value") -> tuple[SchemaProblem, ...]

class Catalog:
    def __init__(self, components: Iterable[ComponentDeclaration], llms: Iterable[LlmEntry]) -> None
    def component(self, ref: ComponentRef) -> ComponentDeclaration | None
    def components(self) -> tuple[ComponentDeclaration, ...]   # platform first, then by type and version
    def llm(self, entry_id: str) -> LlmEntry | None
    def llms(self) -> tuple[LlmEntry, ...]                     # configuration order
```

## Behaviour

- `parse_declaration` validates against
  [component-declaration-1.schema.json](../../../../docs/contracts/schemas/component-declaration-1.schema.json),
  then checks: `config_schema` is a valid draft 2020-12 schema; every `uses` pointer,
  `ui.card` pointer, field `path` and `when.path` resolves in `config_schema`
  (through `properties`, `items` and local `$ref`); a field with control `service`
  names a service and pointer present in `uses`; placement `output` requires
  `outputs_from`; `outputs_from` resolves to an array of strings in `config_schema`;
  section ids are unique; only `number` fields have a `format`. All problems are
  collected into one `DeclarationError`.
  When the declaration does not match its JSON Schema, only those problems are reported.
- The presentation attributes of the contract (section `columns`; field `label_position`,
  `align`, `width` and, for `number` fields, `format`) are validated by the declaration
  schema and kept exactly as declared: absent attributes stay absent, since the interface
  applies their defaults, and `ComponentDeclaration.document`, which the catalog API
  serves as is, carries them to the frontend.
- Each issue is `"<JSON Pointer into the declaration>: <English text>"`, with
  `declaration` for the whole document, for example
  `/uses/0/pointer: "/modle" does not resolve in config_schema`.
- A valid `config_schema` passes the draft 2020-12 metaschema with format assertions (so
  every `pattern` is a valid regular expression), declares no other `$schema` than
  `https://json-schema.org/draft/2020-12/schema`, and has only local `$ref` values
  (`#` plus a JSON Pointer, percent-decoded) that resolve within it. Validation never
  fetches remote references.
- Every JSON Schema `pattern` checked here (the declaration format and the metaschema)
  follows ECMA-262: `$` matches only at the very end of the string, never before a
  final newline.
- Duplicate component references in `Catalog` raise `ValueError`; duplicate LLM ids too.
  `components()` lists Trigger and Output first, then the others by type and by numeric
  version.
- `output_ports(config)` returns `outputs`, or the distinct valid port names found at
  `outputs_from` in `config`, in configured order; it never raises for malformed
  configuration (graph validation reports the problems).
- `llm_entry` generates the parameter schema exactly as the LLM service contract
  specifies: `max_completion_tokens` always, required, with title, bounds and
  default; `reasoning_effort` when more than one effort; `temperature` unless
  unsupported, with the `if`/`else` clause for `without_reasoning`;
  `additionalProperties: false`. A `default_output_tokens` outside 1 to
  `max_output_tokens` raises `ValueError`. `LlmEntry.document()` returns a copy.
- `schema_problems` validates any JSON value against a JSON Schema: draft 2020-12, ECMA-262
  patterns, references never fetched (an unresolvable one is a `$ref` problem at the
  whole value). It returns the distinct problems in validation order, each located at the
  exact offending value: a missing member at its own path, a member rejected by
  `additionalProperties: false` or by a `false` property schema at its path, and a
  property name refused by `propertyNames` at its member's path. The phrase
  maps keywords as graph validation specifies (`minLength` of 1 or `required` → “is
  required”, `type`, `enum`, `minimum`/`maximum`, `pattern`, `maxLength`/`maxItems`,
  others → “is invalid”). The sentence starts with `SchemaProblem.label_of(path, labels,
  fallback)`: the deepest of `labels` containing the path, otherwise a readable form of its
  last property name (`output_format` → `Output format`), otherwise `fallback`; `labels`
  defaults to the `title` of each property of `schema`, nested through `properties`.
  Graph validation builds its `invalid_document`, `invalid_config` and
  `invalid_service_parameters` diagnostics from these problems.
- `parameter_problems` returns the distinct sentences of `schema_problems(parameters
  schema, parameters, fallback="Parameters")`, sorted, for example
  `Max output tokens must be at most 128000.`; empty when the object is valid.
- `with_defaults` returns a copy that adds, in schema order, the `default` of each
  top-level property the object lacks, unless that addition introduces a problem (for
  DeepSeek Flash, no `temperature` when `reasoning_effort` is not `none`). Existing
  values are never changed.
- Platform declarations and the declaration schema are package data files in `_data/`
  equal to the contract examples
  [trigger](../../../../docs/contracts/examples/trigger.component.json) and
  [output](../../../../docs/contracts/examples/output.component.json) and to the
  contract schema; tests assert the equality.

## Acceptance

- The four example declarations parse; the LLM catalog example equals the entries
  generated from the step 1 model settings.
- Each declaration rule above has a failing example with its issue text.
- 100% of public functions are covered; branch coverage of the package is at least 90%.
