# Component preparation commands

Builds reproducible component bundles for explicit installation before experiment execution.

Use the [public entry point](__main__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

First-cycle implementation and local acceptance checks are complete.

`--component all` includes `redirector`, `routed-call` and `bounded-flow` alongside
the existing four components. Their distribution and component versions are
`0.1.0`; the shared host dependency remains exactly `0.1.0.dev1`.

The default Redirector recipe includes the example selector distribution. To use
another authored selector, pass `--selector-project /absolute/project` with
`--component redirector` or `all`. This is an explicit trusted preparation input,
not a graph or invocation argument. The selected project must be a static-version,
src-layout Hatchling package. Its built wheel, source digest and exact package
requirement enter the same hashed production closure and offline installation
workflow. Graph configuration names an installed public `module:callable` only.
No package installation or source loading happens at invocation time.
