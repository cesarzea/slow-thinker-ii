"""The catalog lists platform components first and refuses duplicates."""

import pytest
from slow_thinker_ii.catalog import (
    OUTPUT,
    TRIGGER,
    Catalog,
    ComponentDeclaration,
    ComponentRef,
    llm_entry,
    parse_declaration,
)

from .contract_fixtures import (
    changed,
    declaration_example,
    model_settings,
    step_one_catalog,
    step_one_components,
)


def router(version: str) -> ComponentDeclaration:
    return parse_declaration(changed(declaration_example("router"), ("version",), version))


def test_components_are_ordered_platform_first_then_by_type_and_version() -> None:
    newer, older = router("1.10.0"), router("1.9.0")
    catalog = Catalog([newer, *reversed(step_one_components()), older], [])
    assert [str(item.ref) for item in catalog.components()] == [
        "trigger@1.0.0",
        "output@1.0.0",
        "llm-call@1.0.0",
        "router@1.0.0",
        "router@1.9.0",
        "router@1.10.0",
    ]


def test_lookups() -> None:
    catalog = step_one_catalog()
    trigger = catalog.component(TRIGGER)
    assert trigger is not None and trigger.ref == TRIGGER
    assert catalog.component(OUTPUT) is not None
    assert catalog.component(ComponentRef("router", "2.0.0")) is None
    assert [entry.id for entry in catalog.llms()] == [
        "openai/gpt-6-luna",
        "deepseek/deepseek-flash",
    ]
    flash = catalog.llm("deepseek/deepseek-flash")
    assert flash is not None and flash.provider == "deepseek"
    assert catalog.llm("openai/gpt-5") is None


def test_llms_keep_configuration_order() -> None:
    entries = [llm_entry(settings) for settings in reversed(model_settings())]
    assert [entry.id for entry in Catalog([], entries).llms()] == [
        "deepseek/deepseek-flash",
        "openai/gpt-6-luna",
    ]


def test_duplicate_components_are_refused() -> None:
    with pytest.raises(ValueError, match="^Duplicate component router@1.0.0$"):
        Catalog([router("1.0.0"), router("1.0.0")], [])


def test_duplicate_llm_entries_are_refused() -> None:
    entry = llm_entry(model_settings()[0])
    with pytest.raises(ValueError, match="^Duplicate LLM entry openai/gpt-6-luna$"):
        Catalog([], [entry, entry])
