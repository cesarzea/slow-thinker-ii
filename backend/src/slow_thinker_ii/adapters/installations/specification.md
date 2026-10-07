# adapters.installations: specification

Installed component packages: offline installation from hash-locked wheels,
verification, and loading of each package's [declaration](../../../../../docs/contracts/component-declaration.md).
Implements `LaunchTarget` for `adapters.hosts`.

## Public interface (`slow_thinker_ii.adapters.installations`)

```python
class InstallationCatalog:
    def __init__(self, root: Path, uv: Path, python: Path) -> None   # absolute paths
    def prepare(self, lock: Path, wheels: Path, registration: ComponentRegistration,
                provenance: Mapping[str, JsonValue] | None = None) -> Resolution
    def verify(self, identity: str) -> Resolution
    def interpreter(self, identity: str) -> Path      # the environment's python, verified first

class ComponentRegistration(BaseModel):   # frozen; unknown fields refused
    type: str                             # component type, e.g. "router"
    type_version: str                     # component version, e.g. "1.0.0"
    distribution: str                     # distribution name
    version: str                          # distribution version, e.g. "0.1.0.dev1"
    module: str                           # dotted importable package run with `python -m`

class Resolution(BaseModel):              # the published record, schema_version "2"
    identity: str                         # 32 lowercase hexadecimal digits
    registration: ComponentRegistration
    ...                                   # uv version, lock digest, wheels, files, inspection, provenance

@dataclass(frozen=True)
class InstalledComponent:
    resolution: str                    # resolution identity
    declaration: ComponentDeclaration
    module: str                        # entry module run with `python -m`

class InstalledComponents(LaunchTarget):
    def __init__(self, catalog: InstallationCatalog, resolutions: Sequence[str]) -> None
    def components(self) -> tuple[InstalledComponent, ...]      # verified at construction
    def interpreter(self, ref: ComponentRef) -> Path
    def module(self, ref: ComponentRef) -> str
```

`InstalledComponents` satisfies `LaunchTarget` structurally: the adapters are independent, so
this package does not import `adapters.hosts`.

## Behaviour

- A registration is the `registration.json` written by `tooling/components`:
  `type`, `type_version` (the component version, e.g. `1.0.0`), `distribution`,
  `version` (the distribution version, e.g. `0.1.0.dev1`) and `module`. The
  declaration is the package's `component.json`, shipped as package data inside the
  importable package and read from the installed environment during inspection; it
  must parse with `catalog.parse_declaration`, and its `type` and `version` must equal
  the registration's `type` and `type_version`.
- The describe probe of the previous implementation is removed; nothing in a component
  is executed during installation or inspection.
- `InstalledComponents` verifies every configured resolution once at startup and before
  each launch, as before.

### Preparation and verification

- `prepare` accepts only a complete lock of exact, SHA-256-hashed requirements without
  options, URLs, extras or markers, which must name the registered distribution and version.
  It selects exactly one compatible regular wheel per package, checks its hash and its
  metadata name and version, stages lock and wheels under `<root>/resolutions/<identity>/`,
  installs them with the pinned `uv 0.12.19` (`--offline --no-cache --require-hashes
  --only-binary :all:`, environment `PATH` only), inspects the environment and publishes
  `<root>/catalog/<identity>.json` only when everything matches. A failed preparation
  publishes nothing and leaves earlier resolutions unchanged.
- The inspection is a standalone script run with the environment's isolated interpreter
  (`python -B -I`). It reads distribution metadata only: the registered distribution must
  have the registered version and ship `<module>/__main__.py` and `<module>/component.json`,
  whose text it reports with the interpreter version, platform and installed packages. The
  installed packages must equal the lock and the interpreter must match the backend's.
- `verify` re-reads the record and checks its identity, the lock digest, every retained
  wheel (which must stay inside the resolution), the digest of every installed file and a
  fresh inspection, which must equal the recorded one. Each mismatch raises `ValueError`;
  an installation command that fails raises `RuntimeError` with the end of its output.
- `InstalledComponents` refuses a resolution whose declaration is invalid or does not name
  its registered component, and two resolutions of the same component version
  (`ValueError`); `interpreter` and `module` of a component it does not install raise
  `LookupError`. Verification is synchronous: it runs the inspection and hashes every file.

## Porting

Start from `origin/main` (`backend/src/slow_thinker_ii/adapters/installations/`),
excluding `_contract_probe.py` and `_descriptions.py`. Carry and adapt
`test_installation_integrity.py`, `test_installation_wheels.py`, `test_installations.py`
and `unit/test_installation_locks.py` with `support/installations.py` and `wheels.py`,
placing them under `backend/tests/installations/` (`backend/tests/support/` belongs to F2).

## Acceptance

Tests cover preparation, hash mismatch, tampered environments, declaration loading
and mismatch, and launch targets. Branch coverage at least 90%.
