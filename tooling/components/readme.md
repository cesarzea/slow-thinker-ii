# Component preparation commands

Builds the LLM Call, Router and Memory packages, each with the host SDK, into hash-locked,
provenance-recorded artifacts, then installs them into the platform's installation
catalog, before any run.

```sh
make components   # uv run --locked python -m tooling.components --component all
```

The command prints each installed resolution identity and the list to put into the
server configuration's `components.resolutions`. Preparations, resolutions and the
catalog live under `.local/components/`. See [specification.md](specification.md) for
the artifacts and rules.
