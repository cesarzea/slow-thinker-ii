# Development

Use Node.js 24, Python 3.13 and uv 0.12.17. Install locked dependencies with
`make setup`; run the same checks as CI with `make verify`.

Start `make backend` and `make frontend` in separate terminals, then open
`http://127.0.0.1:5173`. This initial application displays four bundled graphs;
execution controls appear when explicit operator configuration is supplied. The backend imports the public Vercel model
catalogue on startup when missing or overdue, then every 24 hours while running.
Validated rates for the initial OpenAI profile and refresh outcomes persist in
`.local/state.sqlite3`; failures preserve the last valid revision. The read-only
`GET /api/v1/tariffs` endpoint reports its revision, age timestamps and errors.
No API key is required for catalogue downloads. The local POSIX backend holds a
kernel lease beside the canonical database path; a second backend is refused
before migration or recovery. Startup marks unfinished runs interrupted, releases
only unsent reservations and never replays model calls.

SQLite schema v4 includes run, call, ordered event and response receipt records.
Upgrades retain a verified `.v<version>.<identity>.backup` beside the database.
Unfinished v2 runs must be recovered before the receipt-schema upgrade.
`ManagedCalls` connects transactional admission to ready operations: validation,
reservation, dispatch authorization and response settlement. Each billable attempt uses its UTC reservation month, including runs crossing month boundaries; late settlement keeps the original period. Run and session totals continue across months. Nested calls run
outside database transactions. Stop cancels tasks and retains uncertain costs;
bounded cleanup reports work still active. The process adapter is tested against
real MCP children. `ManagedRun` owns readiness, calls, finalization and process
cleanup; `RunProgram` supplies the graph logic. T5 preserves the first Stop
cause, rejects late/incomplete success and retains final outputs atomically.
`SequenceCompiler` validates JSON contracts, pinned type references, resource
permissions and backward data bindings against supplied instance contracts.
`SequenceProgram` executes those plans through the managed controller and node
calls. Tests run all four bundled graphs with a real MCP controller and
simulated agents. `InstalledGraphCompiler` additionally resolves selected installed
classes and their effective contracts; `InstalledGraphEnvironment` starts the
compiled instances with trusted host bindings. Operator command storage now admits runs with saved sessions, frozen configuration
and durable receipts. Trusted application composition exposes authenticated commands, state, history and final results. Browser controls create sessions, start/stop runs and recover command receipts. Recovery of previously orphaned OS processes still
requires stronger persisted process identity; a saved PID alone is not trusted.

The host SDK and sequence controller live in separate packages under
`components/host` and `components/sequence`. Development setup installs them
editably; subprocess tests exercise MCP calls, deadlines and process cleanup.
Run `make components` to prepare the controller, LLMCall, OpenAI resource and
derived reviewer in separate production environments.
This explicit preparation downloads production wheels, generates a hash-pinned
lock, installs offline and publishes a new verified resolution under
`.local/components`. Existing resolutions remain unchanged. uv 0.12.17 is pinned
inside the development environment; pip is used only to fetch locked wheels.
The command prints an immutable bundle file containing the selected resolution
IDs. Check those actual installations explicitly with:

```sh
SLOW_THINKER_TEST_BUNDLE=/absolute/path/to/bundle.json \
  uv run --locked pytest backend/tests/installed/check_bundle.py \
    backend/tests/installed/check_graphs.py \
    backend/tests/installed/check_coordinator.py \
    backend/tests/installed/check_operator.py -q
```

These additional checks run the installed controller, the agent/provider path
including the inherited reviewer, and all four complete example graphs against
local HTTP fixtures. They require no provider credential or paid call and run
separately from the default offline suite,
which tests preparation with synthetic local wheels. `InstalledProcess` retains
the admitted installation record, checks it before launch and verifies integrity
after cleanup. Graph checks obtain contracts from the installed classes and verify
node calls, settled costs and process cleanup. The fixture supplies trusted
provider/limit bindings and now enter through the operator command store;
the production profile loader and HTTP composition are also exercised by the default suite.
`components/llm-call` implements one standard OpenAI SDK call with text/JSON
validation, functional extension hooks and a fresh client and object per MCP
invocation. `examples/grounded-review` is a separate package inheriting that
implementation and checking citation identifiers. Tests use simulated responses
and a real loopback HTTP endpoint; no provider key is needed. All four component targets now support production wheel preparation.

The native Chat Completions router now sends standard OpenAI client calls through
invocation-scoped authorization, frozen model bindings and the managed budget and
receipt path. Tests connect a real independent LLMCall process to that HTTP router
and the independent `components/openai-model` resource, which makes one native
HTTP request to a local simulated provider. The resource receives an explicit
launch credential outside recorded bootstrap data and removes it from its
process environment on startup. It bounds response capture and timeouts, rejects
redirects, disables inherited proxies and redacts reflected credentials.
The OpenAI profile settles complete usage against the retained tariff; missing
usage keeps its reservation. Installed checks exercise production route composition and complete example graphs; live account access has not been tested. Tests use synthetic credentials
and require no paid call.

Browser tests automatically select available ports, so development servers can
remain running during verification.

The [engineering standards](README.md#engineering-standards) are mandatory.
Modules follow the [declared layout](docs/architecture/module-boundaries.md).
Public entry points define supported imports; implementation files and mutable
state remain encapsulated. New source locations must declare a responsibility
in `tooling/locations.json`.

## Enable local execution

Run `make components`, then copy `examples/local-execution.json` to
`.local/execution.json`. Relative paths resolve against the configuration file;
these two directories have the same depth. Replace each zero `resolution_id`
with its corresponding `sequence`, `llm-call` or `openai-model` identity from the
bundle printed by component preparation. Set `review_expires_at` to the UTC Unix
expiry of your reviewed provider profile; the template deliberately starts expired.
Budget amounts are integer billionths of USD: the example caps are USD 0.10 per
run, USD 1 per saved session and USD 5 per UTC month. Adjust them and the time limits
before use. Change `revision` when changing an already activated configuration.

Supply `SLOW_THINKER_OPERATOR_TOKEN` (32–128 URL-safe characters) and `OPENAI_API_KEY`
through your environment. The JSON contains environment-variable names only.
Then start the backend with:

```sh
SLOW_THINKER_CONFIGURATION="$PWD/.local/execution.json" make backend
```

Start `make frontend`, open `http://127.0.0.1:5173`, enter the operator token,
create a saved session, select a graph and supply its task. The interface supports
Start, Stop, history, recorded results and authoritative budget balances.
Use **Inspeccionar ejecución** to follow events to their calls, arguments, responses
and usage. **Ver activación** opens that intervention’s effective input, published
output, input provenance and calls. Evidence pages refresh explicitly and preserve
their paging boundary. It keeps
only unresolved command identities in browser storage; credentials and task text
are not persisted there. Actual execution with this configuration uses your paid
provider account. Automated tests use local fixtures and require no provider key.

## Definition of done

- The requested behavior and failure handling work through public interfaces.
- Relevant unit, contract, integration and browser checks pass.
- Coverage meets every required threshold; budget logic has mutation evidence.
- Each new automated gate rejects a deliberate violation.
- `make verify` passes without suppressed errors or weakened limits.
- Contracts and usage documentation describe implemented behavior accurately.
- Review follows [Google's practices](https://google.github.io/eng-practices/review/).

Use Conventional Commit PR titles and squash messages. Changes to `main` require
an approved pull request and required checks once the remote repository is set
up. Local workflow files do not establish remote branch protection.

Never commit credentials, local databases or provider responses containing
private data. Required CI checks use simulated providers and no provider keys.
Signed releases, provenance and an SBOM apply from the first published release.

The SQLite operator store serializes Start, Stop and withdrawal with durable
receipts. Repeated command identities cannot create new work. Explicit trusted
configuration activation preserves existing budget commitments, and admission
remains closed while an earlier runtime lacks confirmed cleanup. These services
are tested directly and through installed graph runs. Authenticated HTTP commands
and initial state/history projections are implemented; browser execution controls and event/call/payload inspection are implemented; complete internal reporting and diagnostics remain pending.

`ExecutionCoordinator` owns pending commands and accepted runtimes independently
of HTTP request lifetimes. It checks stored receipts before preparation, bounds
preparation/shutdown, routes native model requests with transient authority, and
propagates Stop/withdrawal to live work. The additional installed coordinator
checks cover all four example graphs plus cancellation during a simulated
provider request. These checks use the production `InstalledWorkflowPreparer`,
including installed contracts, effective configuration and frozen tariff evidence.
The application accepts an explicit `ExecutionSetup` for its lifespan, native
gateway and authenticated operator routes. JSON startup configuration and browser execution controls are implemented; these checks need no paid provider credentials.
