# adapters.hosts

Runs component hosts as local processes for one run: writes their bootstrap documents,
launches them isolated and concurrently, checks their readiness over MCP, calls their
`activate` and `select_output` tools within each call's budget, and stops them.

```python
launcher = LocalHostLauncher(installed_components, HostSettings(workspace, llm_url, mcp_url))
hosts = await launcher.launch(run_id, plan, log)  # records host.ready / host.failed
...
await hosts.close()
```

A failed start raises `application.StartupFailed` with an English detail naming the
node and the cause. See [specification.md](specification.md) for the records, failure
codes and limits. Tests: `uv run --locked pytest backend/tests/hosts`.
