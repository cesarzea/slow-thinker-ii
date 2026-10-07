# application: specification

Use cases of S06 and the ports adapters implement. No framework, persistence,
process, network or provider imports.

## Ports (`slow_thinker_ii.application`)

```python
class GraphStore(Protocol):            # branches of working-copy changes, and versions
    # change and version numbers are unique per graph; `branch` is a branch name, `name` the document's
    def create(self, graph_id: str, name: str, document: JsonObject, at: datetime) -> None   # branch "main", change 1; raises GraphExists
    def create_branch(self, graph_id: str, branch: str, name: str, document: JsonObject,
                      from_version: int | None, from_change: int | None, at: datetime) -> int  # its first change; raises BranchExists (ignoring case)
    def add_change(self, graph_id: str, branch: str, name: str, document: JsonObject, at: datetime) -> int  # next change of the graph, on an existing branch
    def branches(self, graph_id: str) -> tuple[BranchSummary, ...]       # oldest first; () for an unknown graph
    def latest_change(self, graph_id: str, branch: str) -> ChangeRecord | None
    def changes(self, graph_id: str, branch: str | None, before: int | None, limit: int) -> tuple[ChangeSummary, ...]  # every branch when None; number < before; newest first
    def change(self, graph_id: str, change: int) -> ChangeRecord | None
    def add_version(self, graph_id: str, change: int, parent: int | None, at: datetime) -> int  # next version of the graph, on the change's branch
    def graphs(self) -> tuple[GraphSummary, ...]          # most recently changed first
    def graph(self, graph_id: str) -> GraphRecord | None  # branches and versions oldest first
    def version(self, graph_id: str, version: int) -> VersionRecord | None

class RunStore(Protocol):
    def create(self, run: RunRecord) -> None             # status "starting"
    def append(self, run_id: str, event: NewEvent) -> RecordedEvent   # assigns the next seq atomically
    def finish(self, run_id: str, status: str, reason: str | None, detail: str,
               totals: JsonObject, at: datetime) -> None
    def run(self, run_id: str) -> RunRecord | None
    def runs(self, graph_id: str | None, limit: int) -> tuple[RunRecord, ...]   # newest first
    def events(self, run_id: str, after: int, limit: int) -> tuple[RecordedEvent, ...]  # seq > after
    def unfinished(self) -> tuple[str, ...]

class Ledger(Protocol):
    def reserve(self, call_id: str, run_id: str, scopes: Sequence[Scope], amount: int,
                at: datetime) -> Scope | None              # returns the exhausted scope, or None when reserved
    def settle(self, call_id: str, charge: int, estimated: bool, at: datetime) -> None
    def used(self, kind: str, key: str) -> int
    def settle_open(self, run_id: str, at: datetime) -> None  # restart recovery: open → reserved, estimated

class HostLauncher(Protocol):
    async def launch(self, run_id: str, plan: RunPlan, log: RunLog) -> RunHosts   # records host.ready / host.failed
class RunHosts(engine.Hosts, Protocol):
    async def close(self) -> None                        # never raises

class LlmProvider(Protocol):
    async def complete(self, model: LlmModel, request: JsonObject, timeout_s: float) -> ProviderReply

class Clock(engine.Clock, Protocol):
    def now(self) -> datetime            # aware UTC
```

```python
@dataclass(frozen=True)
class LlmModel:
    settings: LlmModelSettings  # catalog
    tariff: Tariff  # accounting


@dataclass(frozen=True)
class ProviderReply:
    status: int  # 200 success, 502 provider_error, 504 provider_timeout
    body: JsonObject  # Chat Completions response or {"error": {...}}, redacted
    usage: Usage | None  # normalized; None when unknown
    started_at: datetime  # aware UTC
    ended_at: datetime


@dataclass(frozen=True)
class GatewayReply:
    status: int
    body: JsonObject


@dataclass(frozen=True)
class RunView:
    summary: RunRecord
    results: tuple[JsonObject, ...]  # {"node_id", "name", "payload", "at"}
    activations_by_node: Mapping[str, int]
    messages_by_connection: Mapping[str, int]  # "<from> -> <to>"


@dataclass(frozen=True)
class EventPage:
    events: tuple[RecordedEvent, ...]
    last_seq: int
    finished: bool


@dataclass(frozen=True)
class BudgetLimits:
    daily_nanos: int  # quanta of 10⁻⁹ USD, from budgets.daily_usd
    monthly_nanos: int


@dataclass(frozen=True)
class RunSettings:
    max_active_runs: int = 4
    max_activation_seconds: int = 300
```

The records are frozen dataclasses whose fields are the columns and envelopes of the
[operator API](../../../../docs/contracts/operator-api.md) and the
[recording contract](../../../../docs/contracts/recording.md); `to_json()` returns
their exact API shape, with times as UTC RFC 3339 with milliseconds (`rfc3339(at)`,
exported, refuses naive times):

```python
GraphSummary(id: str, name: str, active_version: int | None, latest_change: int,
             updated_at: datetime)               # name and updated_at of the latest change
BranchSummary(name: str, created_at: datetime, from_version: int | None, from_change: int | None,
              latest_change: int, head_version: int | None)
VersionSummary(version: int, branch: str, parent: int | None, change: int, name: str,
               created_at: datetime)
GraphRecord(id: str, name: str, active_version: int | None, latest_change: int,
            branches: tuple[BranchSummary, ...], versions: tuple[VersionSummary, ...])
VersionRecord(graph_id: str, version: int, branch: str, parent: int | None, change: int,
              created_at: datetime, document: JsonObject)
ChangeSummary(change: int, branch: str, at: datetime, name: str, version: int | None)
ChangeRecord(graph_id: str, change: int, branch: str, at: datetime, document: JsonObject,
             version: int | None)
RunRecord(run_id: str, graph_id: str, version: int | None, change: int, status: str, reason: str | None,
          detail: str, input: JsonValue, created_at: datetime, ended_at: datetime | None,
          totals: JsonObject | None)        # totals None until finished; to_json() omits input
NewEvent(at: datetime, elapsed_ms: int, kind: str, evidence: str, node_id: str | None,
         activation_id: str | None, data: JsonObject)
RecordedEvent(run_id: str, seq: int, + the fields of NewEvent)
```

Errors raised to adapters: `GraphExists(graph_id)`, `GraphNotFound(graph_id)`,
`BranchExists(graph_id, name)`, `BranchNotFound(graph_id, name)`, `InvalidBranch(message)`
(a `ValueError`), `ChangeNotFound(graph_id, change)`, `VersionNotFound(graph_id, version)`, `GraphInvalid` (re-exported from `graphs`, with
diagnostics, also used when a document's `id` differs from the requested graph),
`RunNotFound(run_id)`, `TooManyRuns(limit)`, `InvalidGrant()`, `InvalidReport(message)`
and `StartupFailed(detail)`, which `HostLauncher.launch` raises.

## Use cases

| Class                | Methods                                                                                   |
| -------------------- | ----------------------------------------------------------------------------------------- |
| `GraphLibrary`       | `validate(document) -> tuple[Diagnostic, ...]`; `create(document) -> tuple[str, str, int]` (id, "main", 1); `record_change(graph_id, branch, document) -> tuple[int, datetime, bool]` (change, at, created); `create_branch(graph_id, name, *, from_version=None, from_change=None) -> int` (its first change); `branches(graph_id) -> tuple[BranchSummary, ...]`; `changes(graph_id, branch=None, before=None, limit=50) -> tuple[ChangeSummary, ...]`; `change(graph_id, n) -> ChangeRecord`; `activate(graph_id, change) -> VersionSummary`; `graphs()`; `graph(id) -> GraphRecord`; `version(id, n) -> VersionRecord` |
| `RunService`         | `start(graph_id, version, input, *, change=None) -> str` (async): a version, or with `version=None` a change, whose version (if any) is recorded; `ValueError` without either, `ChangeNotFound` for an absent change; `stop(run_id) -> str`; `stop_for_budget(run_id, scope)`; `run(run_id) -> RunView`; `runs(graph_id, limit)`; `events(run_id, after, limit) -> EventPage`; `recover()`; `shutdown()` (async); `active_call(grant) -> ActiveCall | None` |
| `LlmGateway`         | `complete(grant, body: str) -> GatewayReply` (async), per the LLM service contract       |
| `ReportService`      | `report(grant, kind, content) -> None`, recording reported evidence; `InvalidGrant` otherwise |
| `UsageService`       | `usage() -> JsonObject` shaped as `GET /usage`                                            |

```python
GraphLibrary(store: GraphStore, catalog: Callable[[], Catalog], clock: Clock)
RunService(*, graphs: GraphStore, runs: RunStore, ledger: Ledger, launcher: HostLauncher,
           grants: access.Grants, clock: Clock, catalog: Callable[[], Catalog],
           budgets: BudgetLimits, settings: RunSettings | None = None)
LlmGateway(*, runs: RunService, ledger: Ledger, provider: LlmProvider,
           models: Iterable[LlmModel], budgets: BudgetLimits, clock: Clock)
ReportService(runs: RunService)
UsageService(ledger: Ledger, budgets: BudgetLimits, clock: Clock)
```

`access.Grants` must use the same clock (`Grants(clock.monotonic)`).

Behaviour:

- `GraphLibrary` keeps each graph as a working copy of changes and activated versions
  ([ADR 0024](../../../../docs/adr/0024-working-copy-and-activated-versions.md)). It
  validates with `graphs.validate_document` against the current catalog: changes need only
  a valid draft; activation refuses error diagnostics with `GraphInvalid`.
- `RunService.start` loads the version, compiles the plan (refusing errors), refuses a
  start beyond the active-run limit with `TooManyRuns`, records `run.started`, then
  continues in a background task: launch hosts, run the engine, record `run.finished`
  with totals, close hosts, revoke the run's grants. A launch failure finishes the run
  `failed`, `startup_failed`. The task never raises.
- Active runs are kept in a registry: run id → plan, engine and log. `LlmGateway` and
  `ReportService` resolve grants through `access.Grants` and find the caller's plan
  node there.
- `LlmGateway.complete` checks, in order: grant (`401 invalid_grant`), body shape and
  unsupported fields (`400 invalid_request`), entry selected by the caller
  (`403 model_not_allowed`), parameters against the entry schema (`400`), reservation
  (`402 budget_exhausted`, then `RunService.stop_for_budget`), provider call, settlement,
  `llm.called` record, overrun check. Defaults from the schema fill missing parameters.
- Totals in `run.finished` come from the engine outcome and from the run's `llm.called`
  events: calls, input and output tokens, cost.
- `recover()` marks unfinished runs `failed`, `interrupted`, appending `run.finished`,
  and settles their open reservations as estimated.

## Decided details

- **Threading.** Every use case, the synchronous ones included (`stop`,
  `stop_for_budget`, `report`, `run`, `runs`, `events`), runs on the event-loop thread
  that runs the background tasks: they reach engines and in-flight calls through
  `asyncio` objects, which are not thread-safe. Port methods are synchronous and short.
- **Runs.** Run and call identifiers are `uuid4` hex. `input=None` (absent or JSON null)
  means the Trigger's configured message. `run.started` data: `graph_id`,
  `graph_version`, `input`, `limits` (the graph's four limits, `budget_usd` as a
  nine-decimal string) and `budgets` (`run_usd`, `day_usd`, `month_usd`). The active-run
  limit counts every run whose background task has not ended (starting, running, or
  closing its hosts). The store keeps `starting` until `finish`; `run`, `runs` and `stop`
  report `running` for an active run once `run.running` is recorded.
- **Ending.** In-flight model calls are settled and recorded before `run.finished`
  (see the gateway), then `run.finished` is appended before `RunStore.finish`, so a
  reader that sees a terminal status has every event. Its data: `status`, `reason`,
  `detail`, `totals` (`duration_ms` since admission, `activations` and `messages` from
  the engine outcome, `llm_calls` = every `llm.called` event, `input_tokens` = input +
  cached input + cache write, `output_tokens`, `cost_usd`) and `dropped`, the number of
  `message.dropped` events. A `StartupFailed` launch ends `failed`, `startup_failed` with
  its message as detail; any other launch or engine error ends `failed`,
  `internal_error`. If the store fails, the run stays unfinished for `recover()`.
- **Stops.** `stop` returns the run's current status (`starting` or `running` while
  active, the final status once finished) and raises `RunNotFound` for an unknown run.
  A stop requested while the hosts start is applied as soon as the engine exists (the
  run then ends `cancelled` without `run.running`); a launch failure still ends
  `startup_failed`. `stop_for_budget` details: `The run budget of 0.05 USD is
  exhausted.` (`daily`, `monthly` for the other scopes). `shutdown()` stops every active
  run with `cancelled`, `The platform shut down before the run finished.`, and waits for
  each background task.
- **Queries.** `runs` clamps `limit` to 1–100, `events` to 1–500. `EventPage.last_seq`
  is `after` when the page is empty; `finished` is true only when the run is terminal
  and the page reaches the end of its log. `messages_by_connection` keys are
  `"<node>.<port> -> <node>.<port>"`. `recover()` records `run.finished` with
  `elapsed_ms` measured from the run's `created_at` and totals from its stored events.
- **Library.** A draft is valid when it is a JSON object of at most 1,048,576 serialized
  bytes and `validate_document` reports no `invalid_document` error at the root, `/format`,
  `/id` or `/name`; other diagnostics are allowed. `create` and `record_change` refuse
  other drafts with `GraphInvalid` holding just those diagnostics (size: `The graph
  document is larger than 1 MiB.` at the root). `create` stores branch `main` with change 1
  and no version.
- **Branches.** A name matches `[A-Za-z0-9][A-Za-z0-9 ._-]{0,39}` (ASCII, so uniqueness
  ignoring case agrees with SQLite `NOCASE`) and is unique in the graph ignoring case;
  lookups use the exact name. `create_branch` checks, in order: the name (`InvalidBranch`),
  exactly one of `from_version` and `from_change` (`InvalidBranch`), that it exists
  (`VersionNotFound`, `ChangeNotFound`), then uniqueness (`BranchExists`); the branch's
  first change holds that document. `record_change(graph_id, branch, document)` raises
  `GraphNotFound` or `BranchNotFound` before validating; a different `id` adds
  `invalid_document` at `/id`, `The graph identifier must stay “<id>”; it cannot change
  between versions.`; a document whose compact JSON, keys kept in their order, equals the
  branch's latest change adds nothing and returns `(latest, its at, False)`; key order is
  meaningful (it steers structured LLM output), so a reordered document is a change.
  `changes` filters by branch (`BranchNotFound` for an unknown one), clamps `limit` to
  1–100 and raises `GraphNotFound` for an unknown graph; `change` and `activate` raise
  `ChangeNotFound`. `activate` validates fully and refuses error diagnostics with
  `GraphInvalid`; otherwise it creates the graph's next version on the change's branch
  (again for a change activated before) with `parent` = the branch's head version, or,
  before its first version, the version it started from (None if it started from a change
  or is `main`). The highest version is the active one. A change's `version` is the latest
  version activated from it. Names come from each change's document.
- **Gateway requests.** Accepted top-level fields: `model`, `messages`,
  `response_format`, `stream` only as `false`, `n` only as `1` (both dropped before
  dispatch, so LangChain's defaults work), and the parameter names of any catalog entry's
  schema; anything else is `400` before the model check. Messages have exactly `role`
  (`system`, `user`, `assistant`) and string `content`. `response_format` is
  `{"type": "text" | "json_object"}` or `{"type": "json_schema", "json_schema": {"name",
  "schema"?, "strict"?}}`. A default is added unless it adds a schema violation (DeepSeek's
  `temperature` is left out when `reasoning_effort` is not `none`). Defaults and checks
  are `LlmEntry.with_defaults` and `LlmEntry.parameter_problems` from `catalog`; the 400
  message is `Invalid parameters: ` followed by their sentences, for example
  `Invalid parameters: Max output tokens must be at most 128000.`
- **Gateway records.** Every call whose grant resolves is recorded as `llm.called`,
  rejections (400, 402, 403) included, with `llm`/`provider_model` null when unknown,
  `request` the received body (raw text for 400 shape errors) or the dispatched request,
  `reserved_usd`/`cost_usd` `0.000000000` when nothing was reserved, `rates` as exact
  decimal strings in USD per million tokens with unbilled categories omitted (null when
  usage is unknown) and `duration_ms` from receipt. A missing, unknown, revoked or expired
  grant, including a late use after its call ended, gets `401 invalid_grant` and is not
  recorded, as the component protocol states.
- **Gateway errors.** Bodies are exactly `{"error": {"code", "message", "type"}}` with
  types `invalid_request_error`, `authentication_error`, `budget_error` (402, the message
  names the scope, its limit and the reservation), `permission_error`, `provider_error`
  and `timeout_error`. A provider adapter that raises gives `502 provider_error`.
- **Money.** Scopes are passed with `used=0`; the ledger reads used amounts itself. Day
  and month keys come from `Clock.now()` at the reservation. Usage that `charge` rejects
  is settled as unknown (the reservation, estimated). After a charge above its
  reservation, the first scope whose `used` exceeds its limit stops the run.
- **Provider calls.** `timeout_s` is the time left in the caller's call (its grant's
  deadline); the provider adapter applies the smaller of it and its configured timeout.
  The call runs as a task of its run: when the run ends first it is cancelled and answered
  `504 provider_timeout` (`The run ended before the provider answered.`); when the
  gateway's own request is cancelled, the call is settled and recorded (`504`) before the
  cancellation propagates.
- **Reports.** `kind` is one of `step`, `progress`, `state`, `explanation`, `reasoning`
  and serialized content is at most 65,536 bytes; otherwise `InvalidReport`. Data is
  `{"kind", "content"}` with evidence `reported` for the grant's node and activation.

## Acceptance

Use-case tests with in-memory fakes of every port and the simulated provider cover the
three journeys, the limit case, budget denial at each scope, model not allowed, expired
grant, unsupported fields, invalid parameters, provider error and timeout, unknown
usage, overrun, recovery and the active-run limit. Branch coverage of the package is at
least 90%.
