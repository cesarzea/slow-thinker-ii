# Contributing to Slow Thinker II

Slow Thinker II is early-stage experimental software. Contributions should follow
the agreed scope, public contracts and mandatory
[engineering standards](README.md#engineering-standards).

## Propose a change

For a bug report, include the expected behavior, steps to reproduce, environment
and relevant sanitized diagnostics. For changes to behavior, configuration,
architecture or public contracts, agree the proposal with the maintainer before
implementation. Explain the problem and intended outcome; use a concrete example
when proposing a new interface or format.

## Set up the environment

Use Node.js 24, Python 3.13 and uv 0.12.19, with Git and Make available.
Local process execution requires a POSIX system, such as Linux or macOS.

Clone the repository, or your fork, and install the locked dependencies:

```sh
git clone https://github.com/cesarzea/slow-thinker-ii.git
cd slow-thinker-ii
make setup
```

Setup installs development dependencies and Playwright's Chromium browser.
Install the pinned [CodeQL bundle](tooling/quality/codeql/readme.md#installation)
before running full verification. Automated tests use simulated providers and
require no provider credentials or paid model calls.

See the [local development guide](docs/development.md) to install the components, configure
and start the platform, or enable model execution.

## Implement the change

Create a branch and keep the change focused on its agreed scope. Read the affected
module's documentation and the [architecture and contracts](docs/README.md).

- Follow the [module layout and dependency boundaries](docs/architecture/module-boundaries.md).
  Use public entry points and keep implementation details encapsulated.
- Follow the [module workflow](docs/architecture/module-boundaries.md#module-documents-and-implementation-workflow).
  Keep each affected module's README, specification and pending tasks current.
- Update relevant tests, contracts and usage documentation with the code.
- Write documentation, comments and product-authored text in English.
- Keep credentials, local databases, generated environments and private runtime
  data out of commits, logs and issue attachments.

## Verify the change

Run the shared local and CI verification command from the repository root:

```sh
make verify
```

It includes static analysis, module boundaries, CodeQL, tests, coverage, browser
journeys and accounting mutation checks. All configured checks must pass before
submission. Do not suppress failures or weaken limits to accept a change.

## Submit a pull request

Use a [Conventional Commit](https://www.conventionalcommits.org) title, such as
`fix: preserve reviewer feedback`. Complete the
[pull request template](.github/PULL_REQUEST_TEMPLATE.md): explain the problem,
resulting behavior, verification performed and material limitations.

A change is ready for review when its behavior and failure handling work through
public interfaces, required coverage and checks pass, and affected documentation
matches the implementation. Newly introduced automated gates must demonstrate
that they reject a deliberate violation.

Changes to `main` require a pull request, successful required checks and the
owner's review and merge decision under the
[single-maintainer policy](docs/adr/0012-single-maintainer-review.md).
Reviews follow [Google's engineering practices](https://google.github.io/eng-practices/review/).
Approved pull requests are squash merged with a Conventional Commit message.

## License of contributions

Slow Thinker II is licensed under the [Functional Source License 1.1](LICENSE)
(`FSL-1.1-ALv2`). By submitting a contribution, you confirm that you have the right to
submit it, you license it under the same terms, and you grant Cesar Zea a perpetual,
worldwide, non-exclusive, royalty-free and irrevocable license to use, modify and
license it under other terms, including commercial ones.
