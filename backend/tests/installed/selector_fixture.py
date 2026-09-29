"""Install a packaged nonterminating user selector against the exact retained Redirector wheels."""

import shutil
from pathlib import Path

from slow_thinker_ii.adapters.installations import ComponentRegistration, InstalledDescription
from slow_thinker_ii.contracts import decode_json, encode_json
from support.installations import new_catalog
from support.wheels import lockfile, wheel

from .conftest import PreparedBundle

SOURCE = r"""from slow_thinker_redirector import RedirectorHost
class Host(RedirectorHost): pass
def select(value):
    import sys, signal
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    sys.stderr.write('authorization=Bearer private-selector-token\n')
    sys.stderr.flush()
    while True: pass
"""
CONFIG = (
    '{"outputs":["done"],"selector":"stubborn_selector:select","input_schema":{"type":"object"}}'
)


def selector_installation(
    bundle: PreparedBundle, directory: Path
) -> tuple[Path, InstalledDescription]:
    _, python = bundle.catalog.runtime(bundle.identities["redirector"])
    wheels = python.parents[2] / "wheels"
    artifacts = [
        wheel(directory, "stubborn-selector", "1.0", SOURCE, ("slow-thinker-redirector==0.1.0",))
    ]
    for source in wheels.glob("*.whl"):
        target = directory / source.name
        shutil.copyfile(source, target)
        artifacts.append(target)
    catalog = new_catalog(directory)
    registration = ComponentRegistration(
        type_id="test.selector",
        type_version="1",
        distribution="stubborn-selector",
        version="1.0",
        entry_point="stubborn_selector:Host",
    )
    resolution = catalog.prepare(lockfile(directory, tuple(artifacts)), directory, registration)
    return catalog.interpreter(resolution.identity), catalog.describe(resolution.identity, CONFIG)


def selector_bootstrap(directory: Path, description: InstalledDescription) -> Path:
    contract = description.operations[0]
    path = directory / "bootstrap.json"
    path.write_text(
        encode_json(
            {
                "config": decode_json(CONFIG),
                "operations": [
                    {
                        "name": contract.name,
                        "input_schema": decode_json(contract.input_schema_json),
                        "output_schema": decode_json(contract.output_schema_json),
                    }
                ],
            }
        )
    )
    return path
