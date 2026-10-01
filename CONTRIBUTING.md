# Development

Use Node.js 24, Python 3.13 and uv 0.12.19. Install locked dependencies with
`make setup`; run the same checks as CI with `make verify`.

## CodeQL prerequisite

`make verify` includes the same mandatory CodeQL gate locally and in CI. Install
the official [CodeQL bundle](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/scan-from-the-command-line/set-up-codeql-cli)
at the version in [policy.json](tooling/quality/codeql/policy.json), then set
`CODEQL_EXECUTABLE` to its `codeql` executable or put it on PATH. The documented
project-cache alternative is `.cache/codeql-bundle/<version>/codeql/codeql`.
When using that cache inside this ES-module project, give the cache directory its
own `package.json` with `{"private":true,"type":"commonjs"}` so Node does not apply
the application's module mode to CodeQL's tools.

The runner validates the CLI and bundled queries, checks extraction completeness,
retains SARIF/logs under `.local/verification/codeql`, and rejects errors or warnings.
Notes remain visible. Missing tools and failed/incomplete analysis stop verification;
the gate does not download tools or repeat model calls. CI initializes the same
policy version with the SHA-pinned CodeQL action and passes its public CLI path to
`make verify`. The independent remote CodeQL matrix remains required.

## Local application

Start `make backend` and `make frontend` in separate terminals, then open
`http://127.0.0.1:5173`. The application displays five bundled graphs;
execution controls appear when explicit operator configuration is supplied. The backend imports the public Vercel model
catalogue on startup when missing or overdue, then every 24 hours while running.
Validated rates for the initial OpenAI profile and refresh outcomes persist in
`.local/state.sqlite3`; failures preserve the last valid revision. The read-only
`GET /api/v1/tariffs` endpoint reports its revision, age timestamps and errors.
No API key is required for catalogue downloads. The local POSIX backend holds a
kernel lease beside the canonical database path; a second backend is refused
before migration or recovery. Startup marks unfinished runs interrupted, releases
only unsent reservations and never replays model calls.

SQLite schema v5 includes run, call, ordered event, response receipt, pricing quarantine and owned-process records.
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
calls. Tests run all four finite bundled graphs with a real MCP controller and
simulated agents. `InstalledGraphCompiler` additionally resolves selected installed
classes and their effective contracts; `InstalledGraphEnvironment` starts the
compiled instances with trusted host bindings. Operator command storage now admits runs with saved sessions, frozen configuration
and durable receipts. Trusted application composition exposes authenticated commands, state, history and final results. Browser controls create sessions, start/stop runs and recover command receipts. Restart recovery checks persisted process identity before terminating owned processes. Unconfirmed cleanup blocks new admission; a saved PID alone is not trusted.

The host SDK and sequence controller live in separate packages under
`components/host` and `components/sequence`. Development setup installs them
editably; subprocess tests exercise MCP calls, deadlines and process cleanup.
Run `make components` to prepare Sequence, LLMCall, the OpenAI resource,
GroundedReview, Redirector, RoutedCall and BoundedFlow in separate production environments.
This explicit preparation downloads production wheels, generates a hash-pinned
lock, installs offline and publishes a new verified resolution under
`.local/components`. Existing resolutions remain unchanged. uv 0.12.19 is pinned
inside the development environment; pip is used only to fetch locked wheels.
The command prints an immutable bundle file containing the selected resolution
IDs. Check those actual installations explicitly with:

```sh
SLOW_THINKER_TEST_BUNDLE=/absolute/path/to/bundle.json \
  uv run --locked pytest backend/tests/installed/check_*.py -q
```

These additional checks run the installed controller, the agent/provider path
including the inherited reviewer, and the bundled example graphs against
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
and a real loopback HTTP endpoint; no provider key is needed. All seven component targets support production wheel preparation.

The [bounded-review example](docs/contracts/examples/bounded-review.md) composes an
ordinary reviewer with Redirector using managed MCP calls. A rejection passes the
declared feedback to the next proposal; acceptance returns the final proposal.
For a custom deterministic selector, prepare its trusted Python project with
`uv run --locked python -m tooling.components --component redirector --selector-project /absolute/path/to/project`.
Its callable and declared output ports belong to the component configuration.

The native Chat Completions router now sends standard OpenAI client calls through
invocation-scoped authorization, frozen model bindings and the managed budget and
receipt path. Tests connect a real independent LLMCall process to that HTTP router
and the independent `components/openai-model` resource, which makes one native
HTTP request to a local simulated provider. The resource receives an explicit
launch credential outside recorded bootstrap data and removes it from its
process environment on startup. It bounds response capture and timeouts, rejects
redirects, disables inherited proxies and redacts reflected credentials.
The OpenAI profile settles complete usage against the retained tariff; missing
usage keeps its reservation. Installed checks exercise production route composition and complete example graphs. Automated tests use synthetic credentials
and require no paid call.

Browser tests automatically select available ports, so development servers can
remain running during verification.

The [engineering standards](README.md#engineering-standards) are mandatory.
Modules follow the [declared layout](docs/architecture/module-boundaries.md).
Before implementing a milestone, prepare its [module documents and contracts](docs/architecture/module-boundaries.md#module-documents-and-implementation-workflow): `readme.md`, `specification.md` and a `todo.md` containing only pending work. Remove completed items and delete `todo.md` when empty.
Public entry points define supported imports; implementation files and mutable
state remain encapsulated. New source locations must declare a responsibility
in `tooling/locations.json`.

## Enable local execution

Run `make components`, then copy `examples/local-execution.json` to
`.local/execution.json`. Relative paths resolve against the configuration file;
these two directories have the same depth. Replace each zero `resolution_id`
with its corresponding `sequence`, `llm-call`, `openai-model`, `redirector`,
`routed-call` or `bounded-flow` identity from the
bundle printed by component preparation. Set `review_expires_at` to the UTC Unix
expiry of your reviewed provider profile; the template deliberately starts expired.
Public budget amounts are decimal USD strings with at most nine fractional digits:
the example caps are `"0.100000000"` per run, `"1.000000000"` per saved session and
`"5.000000000"` per UTC month. Internal accounting uses integer billionths of USD.
When migrating an earlier local configuration, convert its integer budget amounts
to equivalent USD strings; do not reinterpret the integers as dollars. Adjust
limits to the authorized allowance before use. Change `revision` when changing an
already activated configuration; retained spending and obligations are not reset.

Supply `SLOW_THINKER_OPERATOR_TOKEN` (32–128 URL-safe characters) and `OPENAI_API_KEY`
through your environment. The JSON contains environment-variable names only.
Then start the backend with:

```sh
SLOW_THINKER_CONFIGURATION="$PWD/.local/execution.json" make backend
```

Start `make frontend`, open `http://127.0.0.1:5173`, enter the operator token,
create a saved session, select a graph and supply its task. The interface supports
Start, Stop, history, recorded results and authoritative budget balances.
Use **Inspect run** to follow events to their calls, arguments, responses
and usage. **View activation** opens that intervention’s effective input, published
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
a pull request, all required checks and the owner's review and merge decision.
The [single-maintainer policy](docs/adr/0012-single-maintainer-review.md) keeps
remote PR and CI enforcement while setting the required external approval count
to zero. Revisit that count when an independent maintainer becomes available.
Local workflow files do not establish remote branch protection.

Never commit credentials, local databases or provider responses containing
private data. Required CI checks use simulated providers and no provider keys.
Signed releases, provenance and an SBOM apply from the first published release.

The SQLite operator store serializes Start, Stop and withdrawal with durable
receipts. Repeated command identities cannot create new work. Explicit trusted
configuration activation preserves existing budget commitments, and admission
remains closed while an earlier runtime lacks confirmed cleanup. These services
are tested directly and through installed graph runs. Authenticated HTTP commands
and initial state/history projections are implemented; browser execution controls and event/call/payload inspection are implemented; optional component reports retain their reported provenance and payload references.

`ExecutionCoordinator` owns pending commands and accepted runtimes independently
of HTTP request lifetimes. It checks stored receipts before preparation, bounds
preparation/shutdown, routes native model requests with transient authority, and
propagates Stop/withdrawal to live work. The additional installed coordinator
checks cover all four finite example graphs plus cancellation during a simulated
provider request. These checks use the production `InstalledWorkflowPreparer`,
including installed contracts, effective configuration and frozen tariff evidence.
The application accepts an explicit `ExecutionSetup` for its lifespan, native
gateway and authenticated operator routes. JSON startup configuration and browser execution controls are implemented; these checks need no paid provider credentials.
