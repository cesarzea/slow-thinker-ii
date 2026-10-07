# Component preparation commands: specification

Builds and installs the S06 component packages before any run. Running a graph never
builds, resolves, downloads or installs code.

## Public boundary

`python -m tooling.components [--component llm-call|router|all] [--destination DIR]`
(`make components`). The defaults are `all` and `.local/components`, the example
configuration's `components.installation_root`; `uv` and the Python interpreter come from
the running environment. The modules are internal to the command:

| Module                         | Provides                                                                                                     |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| `targets`                      | `TARGETS = ("llm-call", "router")`; `target(name) -> PreparationTarget(projects, module)`                    |
| `prepare`                      | `prepare_component(root, destination, uv, python, name) -> Preparation(directory, registration, provenance)` |
| `registration`                 | `Registration(type, type_version, distribution, version, module)`; `read_registration(wheels, module)`       |
| `install`                      | `install(preparation, root, uv, python) -> Resolution`                                                       |
| `build`, `artifacts`, `bundle` | Wheel builds and hashes, recorded inputs and provenance, the bundle file                                     |

## Required behavior

- Each target is built with the host SDK: projects `components/host` and
  `components/<name>`, module `slow_thinker_<name>`.
- Wheels are built with the locked Hatchling in an isolated interpreter with a fixed
  `SOURCE_DATE_EPOCH`; a source change during a build or a duplicate project name is
  an error.
- The registration is read from the built wheel that ships `<module>/component.json`:
  type and version from the declaration (format `slow-thinker.component/1`),
  distribution and version from the wheel metadata. The wheel must also ship
  `<module>/__main__.py`.
- The single requirement `distribution==version` is resolved by the pinned uv into a
  hash-locked closure of binary wheels, which pip downloads with `--require-hashes`;
  first-party wheels must not be replaced by the download.
- Each preparation directory `DIR/preparations/<id>/` holds `wheels/`,
  `requirements.in`, `requirements.txt`, `provenance.json` (source and wheel hashes,
  Hatchling, pip and uv versions) and `registration.json`.
- Each preparation is then installed with `adapters.installations`:
  `InstallationCatalog(DIR, uv, python).prepare(lock, wheels, registration, provenance)`,
  where `registration = ComponentRegistration.model_validate_json(<registration.json>)`.
  The installation is offline and publishes `DIR/catalog/<identity>.json`.
- The command prints `Installed <type>@<version> (<distribution> <version>): <identity>`
  for each component, writes a bundle `DIR/bundles/<id>.json` (schema version 3: the
  installation root and, per component, its resolution, registration and preparation),
  and ends with the line `Put these identities into components.resolutions: [...]`.
- Prepared and installed artifacts contain no provider credentials.

## Dependencies and ownership

Component source packages, the pinned packaging tools and
[`adapters.installations`](../../backend/src/slow_thinker_ii/adapters/installations/specification.md).

## Acceptance criteria

- Preparations of both targets are exact closures of the component and the host SDK,
  every wheel matches a hash in the lock, and provenance and registration are recorded.
- Both components install into the catalog, whose resolutions verify.
- The real component wheels ship declarations equal to the contract examples.
- Rebuilding another component does not replace the artifacts of an earlier
  preparation or resolution.
