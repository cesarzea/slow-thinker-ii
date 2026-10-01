# Slow Thinker II

> **Early-stage experimental software.** Local execution is available; no stable release is available.

**A new implementation of Slow Thinker with customizable agents, components, and collaboration graphs.**

**Original Slow Thinker (previous version):** [Project website](https://www.cesarzea.com/slow-thinker) · [Source code](https://github.com/cesarzea/slow-thinker) · [Example experiment report](https://www.cesarzea.com/assets/slow-thinker/reports/d7442a5f-fd3b-438a-8816-91f4625f2492/report.html#process)

## Principles

- **Configurable, dynamic graphs.** Each experiment defines its own collaboration graph, which can change during execution.
- **Extensible components.** Agents, resources, memory providers, flow controllers,
  and collaboration techniques can be supplied by users through defined contracts.
- **Mediated communication.** The platform routes MCP calls between components,
  controls access, records interactions, and applies execution limits.
- **Optional memory and context.** Resources can be private or shared. Each agent
  determines what context it sends.
- **Observable execution.** Graphs are visible from the first version, with
  inspectable calls, outputs, errors, duration, and cost.
- **Explicit limits.** Configurable call and run deadlines, with spending budgets
  per run, saved work session, and month.
- **Small functional releases.** Start locally with trusted components and simple
  workflows, while preserving room for richer execution models.

## Documentation

- [Architecture and specification](docs/README.md)
- [Architecture decisions](docs/adr/README.md)
- [Contracts and examples](docs/contracts/README.md)
- [Engineering process improvement](docs/continuous-improvement/README.md)
- [Open questions](docs/specification/open-questions.md)

## Current Status

The local prototype runs five bundled graphs, including a proposer–reviewer loop
with conditional feedback. It records calls, results and costs, with configurable
execution limits. Graph editing and collaboration analysis are future work.

## Engineering standards

**These standards are mandatory from the first implementation.** Quality gates are part of the initial repository setup and must be in place before application code is accepted. Automated quality gates run locally and in CI; remote protections are established when the repository is published.

**Architecture and code**

| Standard | Requirement |
| --- | --- |
| Architecture documented with [arc42](https://arc42.org) and [C4](https://c4model.com); decisions recorded as [MADR](https://adr.github.io/madr/) architecture decision records. | Required |
| Directories organized by capability and responsibility; explicit public APIs, encapsulated state, and repository checks for permitted file locations. | Required |
| Module boundaries checked by [dependency-cruiser](https://github.com/sverweij/dependency-cruiser): public entry points only, no cycles, no undeclared or development dependencies in production code | Required |
| TypeScript [`@tsconfig/strictest`](https://github.com/tsconfig/bases); `any` forbidden | Required |
| [typescript-eslint](https://typescript-eslint.io) `strict-type-checked` + `stylistic-type-checked`, SonarJS cognitive complexity | Required |
| Tests with [Vitest](https://vitest.dev) and ≥ 90 % coverage | Required |
| Small units: files ≤ 150 lines, functions ≤ 30 lines, cyclomatic complexity ≤ 8 | Required |
| Dead-code detection with [knip](https://knip.dev): no unused files, exports or dependencies | Required |
| [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html) conventions (named exports only); Prettier formatting | Required |
| Python dependency contracts checked with [Import Linter](https://import-linter.readthedocs.io/en/stable/): no source cycles or imports of module internals; domain independent of frameworks and providers. | Required |
| Python: [Pyright](https://microsoft.github.io/pyright/) strict mode, [Ruff](https://docs.astral.sh/ruff/) linting and formatting; no `Any` in domain code. | Required |
| Python tests with [pytest](https://docs.pytest.org/en/stable/) and [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/): ≥ 90% for lines and branches. TypeScript coverage thresholds apply independently to lines, branches, functions, and statements. | Required |
| Contract and integration tests for components, permissions, budgets, and cancellation; browser journeys with [Playwright](https://playwright.dev/). Required CI tests use simulated model providers. | Required |
| Python dead-code checks with [Vulture](https://github.com/jendrikseipp/vulture). | Required |

**Security and supply chain**

| Standard | Requirement |
| --- | --- |
| [CodeQL](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-query-suites) `security-and-quality` analysis for Python and TypeScript on pull requests. | Required |
| [OpenSSF Scorecard](https://scorecard.dev) assessment published on changes to `main`. | Required |
| GitHub Actions pinned by commit SHA; least-privilege workflow tokens. | Required |
| Secret scanning with push protection and private vulnerability reporting. | Required |
| Committed dependency lockfiles, vulnerability alerts, and automated updates with [Dependabot](https://docs.github.com/en/code-security/dependabot). | Required |

**Process**

| Standard | Requirement |
| --- | --- |
| Protected `main`: pull requests only, required checks, owner review under [ADR 0012](docs/adr/0012-single-maintainer-review.md), linear history, and squash merges. | Required |
| Code review following [Google's engineering practices](https://google.github.io/eng-practices/review/), with a documented definition of done. | Required |
| [Conventional Commits](https://www.conventionalcommits.org) through validated pull request titles and squash commit messages. | Required |
| One verification command locally and in CI; each automated gate must fail on a deliberate violation when introduced. | Required |

Rules must not be weakened merely to make a change pass. Exceptions require a documented rationale and a reviewed architecture decision.

**Assurance and releases**

| Standard | Requirement |
| --- | --- |
| Threat model and mitigations mapped to the [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/). | Required |
| [OWASP ASVS](https://owasp.org/projects/asvs) Level 2 requirements guide the design; verification is required before the first server deployment. | Required |
| Signed releases with [SLSA](https://slsa.dev/) provenance and a [CycloneDX](https://cyclonedx.org/) software bill of materials, starting with the first release. | Required |
| [OpenSSF Best Practices](https://www.bestpractices.dev/en) criteria and badge assessment; mutation testing from the first implementation of budget accounting. | Required |

## Development

Technology stack: **Python + FastAPI** for the backend; **React + TypeScript, React Flow,
and Vite** for the browser interface. MCP and OpenAI-compatible interfaces
support integration with agent tooling, including LangChain and LangGraph.

See the [development instructions](CONTRIBUTING.md) and [verification record](docs/verification.md) for setup, tested behavior and current limitations. The complete platform remains under development.

The [Changelog](CHANGELOG.md) records development progress and sprint report versions.

## License

[Apache License 2.0](LICENSE). Copyright 2026 Cesar Zea.
