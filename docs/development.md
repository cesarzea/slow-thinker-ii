# Local development and operation

This guide covers running the step 1 platform on one machine. For contribution rules
and complete verification, see [CONTRIBUTING.md](../CONTRIBUTING.md).

## Prepare the environment

Install Node.js 24, Python 3.13, uv 0.12.19, Git and Make on Linux or macOS, then run
`make setup` from the repository root. Automated tests use the simulated provider and
need no provider credentials or paid model calls.

## Install the components

LLM Call, Router and Memory run as separate processes from installed packages:

```sh
make components
```

The command builds the component wheels, resolves their dependencies into a
hash-locked set of wheels (this step needs network access), installs each component
offline under `.local/components` and verifies it. It ends with the line
`Put these identities into components.resolutions: [...]`. Running a graph never
installs or downloads code.

## Configure the server

Copy [the example configuration](../examples/server-configuration.json) to
`.local/server-configuration.json` and set `components.resolutions` to the printed
identities. The [bootstrap specification](../backend/src/slow_thinker_ii/bootstrap/specification.md)
describes every field. Relative paths resolve against the directory the server starts
in; run it from the repository root.

- `llm` lists the providers and models offered to graphs, each model with its
  reviewed tariff. To run without provider credentials, replace `providers` with
  `{"simulated": {}}` and set each model's `provider` to `simulated`; a simulated model
  may list scripted `replies`.
- `budgets` sets the daily and monthly spending limits in USD. Each graph sets its run
  budget in its Limits.
- `server.static_directory` serves the built interface. Build it with `npm run build`,
  or set it to `null` and use the development server below.

A database written by the previous implementation is refused with a message. Move it
away or name another `database` path.

## Start the server

Set the environment and start the backend:

```sh
export SLOW_THINKER_CONFIGURATION=.local/server-configuration.json
export SLOW_THINKER_OPERATOR_TOKEN='<32 to 128 visible characters, no spaces>'
export OPENAI_API_KEY='<key>' DEEPSEEK_API_KEY='<key>'   # for configured real providers
make backend
```

Open <http://127.0.0.1:8000> and connect with the operator token. Provider keys stay
in the backend process; component processes receive only an invocation grant per
call. A configuration, credential or installation problem stops startup with a message
that names the field or variable, never a secret.

For interface development, set `static_directory` to `null` and also run
`make frontend`, then open <http://127.0.0.1:5173>. The development server forwards
`/api` to the backend.

## Spending

Every model call reserves its largest possible cost against the run, daily and
monthly budgets before it is sent; a denied reservation stops the run and names the
budget. The banner shows the day's and month's spending. Costs use the tariffs in the
configuration, so review them against the providers' current prices before running
real models.
