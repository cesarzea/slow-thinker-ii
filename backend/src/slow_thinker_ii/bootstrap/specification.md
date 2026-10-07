# bootstrap: specification

Server configuration, environment secrets and the composition root. Nothing imports it.

## Public interface (`slow_thinker_ii.bootstrap`)

```python
def configured_app() -> FastAPI      # uvicorn factory; reads SLOW_THINKER_CONFIGURATION
def create_app(configuration: ServerConfiguration, environment: Mapping[str, str],
               overrides: AppOverrides | None = None) -> FastAPI
def load_configuration(path: Path) -> ServerConfiguration

@dataclass(frozen=True)
class AppOverrides:                   # for tests and browser journeys only
    components: Sequence[ComponentDeclaration] | None = None   # replaces installed declarations
    launch_targets: LaunchTarget | None = None                 # replaces installed environments
    provider: LlmProvider | None = None                        # replaces configured providers

@dataclass(frozen=True)
class ServerConfiguration:            # the validated document, paths absolute
    database: Path; workspace: Path; server: ServerSection; components: ComponentsSection
    providers: tuple[ProviderSection, ...]          # openai and deepseek, when configured
    replies: Mapping[str, tuple[str, ...]]          # scripted replies of simulated models
    models: tuple[LlmModel, ...]; budgets: BudgetLimits; runtime: RuntimeSection
```

Browser journeys use overrides to run the development environment's component
packages as hosts and the simulated provider with scripted replies, without
`make components`. With `provider` overridden, provider credentials are not read;
with `components` and `launch_targets` overridden, no installation is verified.
`backend/tests/journeys/app.py` is the reference use of these overrides. `components`
lists package declarations only; the platform's Trigger and Output are always added.

## Server configuration

A JSON document of at most 1 MiB; the file `slow-thinker.keys.json` is refused. The
[example](../../../../examples/server-configuration.json) is the S06 reference.

| Field           | Content                                                                                     |
| --------------- | ------------------------------------------------------------------------------------------- |
| `database`      | Path of the SQLite file                                                                      |
| `workspace`     | Directory for per-run host files                                                             |
| `server`        | `public_url` (for component callbacks), `allowed_hosts`, `allowed_origins`, `static_directory` (path or `null`), `operator_authentication` (`"token"`, the default, or `"none"`) |
| `components`    | `installation_root`, `uv`, `python`, `resolutions`: installed resolution identities          |
| `llm`           | `providers` and `models` as in the LLM service contract, each model with its `tariff`; provider `simulated` allowed, with optional `replies` |
| `budgets`       | `daily_usd`, `monthly_usd`                                                                   |
| `runtime`       | `max_active_runs` (4), `max_activation_seconds` (300), `host_startup_seconds` (20)          |

Details of the document:

- Unknown members are refused everywhere and JSON types are not coerced. `allowed_hosts`
  needs at least one host; `allowed_origins` (default `[]`), `static_directory` (default
  `null`) and `resolutions` (default `[]`) may be omitted, as may `runtime` and each of its
  members (from 1 to 64 runs, 1 to 86,400 seconds per activation, more than 0 and at most
  600 seconds of host startup).
- `public_url` is an origin, `http(s)://host[:port]` without path, query or credentials;
  a trailing slash is dropped. Hosts call `<public_url>/v1` and `<public_url>/mcp`.
- `operator_authentication` `"none"` serves the operator API without a token, for a local
  server. It is accepted only when every `allowed_hosts` entry is a loopback host,
  `127.0.0.1`, `localhost` or `[::1]`, with an optional port; otherwise loading fails with
  `Invalid server configuration: /server/operator_authentication: "none" requires every
  allowed host to be a loopback address.` The `Host` check does not bind the server: run
  it on a loopback interface (as `make backend` does) when the token is off.
- Relative paths (`database`, `workspace`, `static_directory`, `installation_root`, `uv`,
  `python`) are taken from the working directory when the configuration is loaded; the
  example is written for the repository root.
- `llm.providers` may hold `openai` and `deepseek`, each `{"base_url", "credential_env",
  "timeout_seconds"}` (`credential_env` matches `^[A-Z_][A-Z0-9_]*$`, timeout 120 by
  default, at most 3,600), and `simulated`, an empty object: it has no endpoint and no
  credential. Every model's `provider` must be configured, model ids are unique,
  `default_output_tokens` does not exceed `max_output_tokens`, `reasoning_efforts` may be
  empty, and the `tariff` must parse with `accounting.parse_tariff`. `replies`, a list of
  strings, is allowed only on a model whose provider is `simulated`; the simulated provider
  cycles through them for that model.
- Budgets are decimal USD strings read with `accounting.parse_usd`.
- `resolutions` are not checked when the document is loaded; installed resolutions are
  verified when the application is created.

Every invalid document raises `ValueError`: `Invalid server configuration: <JSON Pointer>:
<reason>.` for each invalid location, `The server configuration is not valid JSON: …`,
`The server configuration must not exceed 1 MiB.` or `Cannot read the server configuration
<path>: …`. Messages never repeat a configured value that could be a secret.

Environment: `SLOW_THINKER_CONFIGURATION`, `SLOW_THINKER_OPERATOR_TOKEN` and each
provider's `credential_env`. A missing credential for a configured provider fails
startup with a message naming the variable, never its value. The operator token must have
32 to 128 visible ASCII characters without spaces; with `operator_authentication` `"none"`
it is not read, and its absence is not an error. Credentials are read from the
`environment` given to `create_app`; `configured_app` passes the process environment.

## Composition

`create_app` builds the catalog (platform declarations, installed declarations, LLM
entries), the stores, grants, provider registry, host launcher and use cases, and the
HTTP app with a lifespan that takes the database ownership lock, initializes the
schema, runs `RunService.recover()`, and on shutdown stops active runs and closes their
hosts.

- Before composing anything it reads the operator token (with `"none"`, it passes
  `operator_token=None` to `HttpSettings`, meaning no operator authentication) and checks
  that a configured `static_directory` exists (`The interface directory <path> does not exist. Build it with
  "npm run build", or set server.static_directory to null.`); a host or origin that the
  HTTP adapter's `HttpSettings` refuses is reported at `/server`. Then, unless `provider`
  is overridden, it reads the provider credentials.
- Providers: one dispatch implements `LlmProvider` for the gateway. Models of provider
  `simulated` go to one `SimulatedProvider` with the configured replies; every other model
  goes to one `HttpProvider` with a `ProviderEndpoint` per configured network provider
  (endpoint errors become `The <provider> provider cannot be used: …`).
- Components: unless both `components` and `launch_targets` are overridden,
  `InstalledComponents` verifies the configured resolutions with an `InstallationCatalog`
  on `installation_root`, `uv` and `python`; its declarations join the catalog and it is the
  launch target, each replaced by its override when given.
- One `SystemClock` (aware UTC `now`, `time.monotonic`) serves every use case and
  `access.Grants(clock.monotonic)`. `LocalHostLauncher` gets `HostSettings(workspace,
  <public_url>/v1, <public_url>/mcp, startup_seconds=host_startup_seconds)`. `RunService`
  gets `RunSettings(max_active_runs, max_activation_seconds)`.
- The lifespan, on the event loop: `ownership()`, `initialize()`, create the workspace,
  `RunService.recover()`, serve, then `await RunService.shutdown()`. A second backend on
  the same database fails at startup with `RuntimeError`.
- `configured_app` ends the process with `Slow Thinker II cannot start: <reason>` (a
  `SystemExit`, no traceback) when the configuration, a secret or an installation is
  invalid, including a missing `SLOW_THINKER_CONFIGURATION`.

## Porting

`read_document` from `origin/main` `bootstrap/_configuration.py` (size cap and refused
file name) and `EnvironmentSecrets` from `adapters/preparation/_secrets.py`. Carry and
adapt `test_startup_configuration.py`.

## Acceptance

Tests cover every configuration error, credential handling, and an application built
from the example configuration with the simulated provider answering the operator API.
