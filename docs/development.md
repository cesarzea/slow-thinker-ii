# Local development

This guide covers running the local application and enabling experiment execution.
For contribution requirements and full verification, see
[CONTRIBUTING.md](../CONTRIBUTING.md).

## Start the application

After `make setup`, run these commands in separate terminals:

```sh
make backend
```

```sh
make frontend
```

Open <http://127.0.0.1:5173>. The backend listens on port 8000; the interface
shows five bundled graphs. Execution controls require the explicit configuration
below. Browser tests select available ports independently, so development servers
can remain running during verification.

The backend downloads the public Vercel model catalogue when it is missing or
outdated, then refreshes it every 24 hours while running. Catalogue downloads
require network access but no provider key. Validated tariffs and refresh outcomes
persist in `.local/state.sqlite3`; failures retain the last valid revision.
`GET /api/v1/tariffs` reports the retained revision, timestamps and refresh errors.

## Prepare component environments

Experiment execution uses independently installed components. Prepare them with:

```sh
make components
```

This command downloads production wheels, creates hash-pinned locks, installs
offline and verifies the environments under `.local/components`. It prepares
Sequence, LLMCall, the OpenAI resource, GroundedReview, Redirector, RoutedCall and
BoundedFlow. Existing installation resolutions remain immutable. The command
prints the path to a bundle containing the selected resolution identifiers.

See [component preparation](../tooling/components/readme.md) for supported recipes
and custom deterministic Redirector selectors. Preparation is an explicit trusted
operation; graph execution does not install packages.

## Configure model execution

1. Copy [the execution template](../examples/local-execution.json) to
   `.local/execution.json`:

   ```sh
   cp examples/local-execution.json .local/execution.json
   ```

2. Replace each zero `resolution_id` with the matching identity from the prepared
   bundle: `sequence`, `llm-call`, `openai-model`, `redirector`, `routed-call` and
   `bounded-flow`. Relative paths resolve against the configuration file; the
   template and `.local` directory have the same depth.
3. Review the provider profile and set `review_expires_at` to its expiry as a UTC
   Unix timestamp. The template deliberately starts expired.
4. Set the deadlines, call limits and budgets for the intended execution. Budget
   values are decimal USD strings with at most nine fractional digits. The template
   allows USD 0.10 per run, USD 1.00 per saved session and USD 5.00 per UTC month.
5. Supply `SLOW_THINKER_OPERATOR_TOKEN` and `OPENAI_API_KEY` through your environment.
   The operator token must contain 32–128 URL-safe characters. Keep the JSON's
   credential references as environment-variable names.

Restart the backend with the configuration enabled:

```sh
SLOW_THINKER_CONFIGURATION="$PWD/.local/execution.json" make backend
```

Start the frontend if needed, then enter the operator token in the interface.
Create a saved session, select a graph, provide its task and start execution.
**Actual model execution uses your paid provider account.**

Change the configuration's `revision` when modifying an already activated
configuration. Existing spending and outstanding obligations remain in force.
For an older configuration using integer budget amounts, convert them from
billionths of USD to equivalent decimal USD strings; do not interpret them as
whole dollars.

## Inspect an execution

Use **Inspect run** to follow recorded events to their calls, arguments, responses
and usage. **View activation** shows an agent intervention's effective input,
published output, input provenance and calls. History retains completed runs,
results and budget balances. Evidence pages refresh explicitly and retain their
paging boundary.

The browser retains only unresolved command identities in local storage. It does
not persist credentials or task text there. Runtime evidence may contain private
inputs and responses; keep local data outside version control.

## Check installed components

The default verification suite checks environment preparation using synthetic
local wheels. After `make components`, also check the actual installations:

```sh
SLOW_THINKER_TEST_BUNDLE=/absolute/path/to/bundle.json \
  uv run --locked pytest backend/tests/installed/check_*.py -q
```

Use the bundle path printed by preparation. These additional checks exercise
installed components and bundled graphs against local HTTP fixtures; they require
no provider credential or paid call. They run separately from `make verify`.

## Local state and recovery

The backend stores local state in `.local/state.sqlite3` and permits one active
backend per database. Stop the existing backend before starting another against
the same database. Schema upgrades retain a verified backup beside the database.
Unfinished schema-v2 runs require recovery before the receipt-schema upgrade.

After a restart, unfinished runs are marked interrupted; model calls are never
replayed automatically. Uncertain costs remain reserved. New execution stays
blocked until earlier process cleanup is confirmed.

For the implemented recovery and accounting rules, see the
[application composition contract](../backend/src/slow_thinker_ii/bootstrap/specification.md),
[SQLite contract](../backend/src/slow_thinker_ii/adapters/sqlite/specification.md)
and [verification record](verification.md).
