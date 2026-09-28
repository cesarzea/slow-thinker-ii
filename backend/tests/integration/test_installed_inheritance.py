"""Real class inheritance and distribution constraints both govern compatible updates."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import ComponentRegistration, ImplementationBase
from support.installations import new_catalog
from support.wheels import lockfile, wheel


def registration(
    base_version: str, requirement: str = "sample-base>=1.1,<2"
) -> ComponentRegistration:
    return ComponentRegistration(
        type_id="test.child",
        type_version="1",
        distribution="sample-child",
        version="1.0",
        entry_point="sample_child:Child",
        base=ImplementationBase(
            distribution="sample-base",
            version=base_version,
            entry_point="sample_base:Base",
            requirement=requirement,
        ),
    )


def test_compatible_update_preserves_old_environment_and_rejects_new_major(tmp_path: Path) -> None:
    catalog = new_catalog(tmp_path)
    child = wheel(
        tmp_path,
        "sample-child",
        "1.0",
        "from sample_base import Base\nclass Child(Base): pass\n",
        ("sample-base>=1.1,<2",),
    )
    first = wheel(tmp_path, "sample-base", "1.1", "class Base: pass\n")
    one = catalog.prepare(lockfile(tmp_path, (child, first)), tmp_path, registration("1.1"))
    second = wheel(tmp_path, "sample-base", "1.2", "class Base: pass\n")
    two = catalog.prepare(lockfile(tmp_path, (child, second)), tmp_path, registration("1.2"))
    assert one.identity != two.identity
    assert catalog.verify(one.identity).inspection.packages["sample-base"] == "1.1"
    assert catalog.verify(two.identity).inspection.packages["sample-base"] == "1.2"
    major = wheel(tmp_path, "sample-base", "2.0", "class Base: pass\n")
    with pytest.raises(RuntimeError, match="Installation command failed"):
        catalog.prepare(lockfile(tmp_path, (child, major)), tmp_path, registration("2.0"))
    assert catalog.verify(one.identity).files == one.files
    assert len(list((tmp_path / "installations/catalog").glob("*.json"))) == 2


@pytest.mark.parametrize(
    "source", ["class Child: pass\n", "from sample_base import Base as Child\n"]
)
def test_metadata_cannot_fake_class_inheritance(tmp_path: Path, source: str) -> None:
    catalog = new_catalog(tmp_path)
    base = wheel(tmp_path, "sample-base", "1.1", "class Base: pass\n")
    child = wheel(tmp_path, "sample-child", "1.0", source, ("sample-base>=1.1,<2",))
    with pytest.raises(RuntimeError, match="Installation command failed"):
        catalog.prepare(lockfile(tmp_path, (base, child)), tmp_path, registration("1.1"))
    assert not (tmp_path / "installations/catalog").exists()


def test_registration_must_match_actual_dependency_constraint(tmp_path: Path) -> None:
    catalog = new_catalog(tmp_path)
    base = wheel(tmp_path, "sample-base", "1.1", "class Base: pass\n")
    child = wheel(
        tmp_path,
        "sample-child",
        "1.0",
        "from sample_base import Base\nclass Child(Base): pass\n",
        ("sample-base>=1.1,<2",),
    )
    with pytest.raises(ValueError, match="differs from installed package metadata"):
        catalog.prepare(
            lockfile(tmp_path, (base, child)), tmp_path, registration("1.1", "sample-base==1.1")
        )
