"""The step 1 declarations parse, platform declarations equal the contract, ports are effective."""

from dataclasses import replace
from importlib.resources import files

import pytest
from slow_thinker_ii.catalog import (
    OUTPUT,
    TRIGGER,
    ComponentRef,
    ServiceUse,
    parse_declaration,
    platform_declarations,
)
from slow_thinker_ii.contracts import JsonObject, JsonValue

from .contract_fixtures import CONTRACTS, changed, declaration_example


def test_the_four_example_declarations_parse() -> None:
    llm_call = parse_declaration(declaration_example("llm-call"))
    assert llm_call.ref == ComponentRef("llm-call", "1.0.0")
    assert (llm_call.label, llm_call.placements, llm_call.stateful) == ("LLM Call", {"node"}, False)
    assert (llm_call.inputs, llm_call.outputs, llm_call.outputs_from) == (("in",), ("out",), None)
    assert llm_call.uses == (ServiceUse("llm", "/model"),)
    assert [use.service for use in llm_call.uses] == ["llm"]
    example = declaration_example("llm-call")
    assert llm_call.config_schema == example["config_schema"]
    assert llm_call.initial_config == example["initial_config"]
    assert llm_call.document == example
    router = parse_declaration(declaration_example("router"))
    assert (router.placements, router.outputs, router.outputs_from) == (
        {"node", "output"},
        None,
        "/outputs",
    )
    trigger = parse_declaration(declaration_example("trigger"))
    output = parse_declaration(declaration_example("output"))
    assert (trigger.ref, trigger.inputs, trigger.outputs) == (TRIGGER, (), ("out",))
    assert (output.ref, output.inputs, output.outputs) == (OUTPUT, ("in",), ())


def test_stateful_declarations() -> None:
    stateful = changed(declaration_example("llm-call"), ("state",), "stateful")
    assert parse_declaration(stateful).stateful is True


def test_platform_declarations_equal_the_contract_examples() -> None:
    trigger, output = platform_declarations()
    assert (trigger.ref, output.ref) == (TRIGGER, OUTPUT)
    assert trigger.document == declaration_example("trigger")
    assert output.document == declaration_example("output")


@pytest.mark.parametrize(
    ("package", "name"),
    [
        ("slow_thinker_ii.catalog", "component-declaration-1.schema.json"),
        ("slow_thinker_ii.graphs", "graph-document-1.schema.json"),
    ],
)
def test_packaged_schemas_equal_the_contract_schemas(package: str, name: str) -> None:
    packaged = files(package).joinpath("_data", name).read_bytes()
    assert packaged == (CONTRACTS / "schemas" / name).read_bytes()


def router_ports(config: JsonObject) -> tuple[str, ...]:
    return parse_declaration(declaration_example("router")).output_ports(config)


@pytest.mark.parametrize(
    ("outputs", "ports"),
    [
        (["accepted", "revise"], ("accepted", "revise")),
        (["yes", "Not ok", "yes", 5, "no", None], ("yes", "no")),
        ([], ()),
        ("yes", ()),
        ({"yes": True}, ()),
    ],
)
def test_configured_output_ports(outputs: JsonValue, ports: tuple[str, ...]) -> None:
    assert router_ports({"outputs": outputs, "script": "x"}) == ports


def test_output_ports_never_raise_for_missing_configuration() -> None:
    assert router_ports({}) == ()
    llm_call = parse_declaration(declaration_example("llm-call"))
    assert llm_call.output_ports({"outputs": ["ignored"]}) == ("out",)
    portless = replace(llm_call, outputs=None, outputs_from=None)
    assert portless.output_ports({"outputs": ["ignored"]}) == ()


def test_component_references() -> None:
    assert ComponentRef.parse("llm-call@1.0.0") == ComponentRef("llm-call", "1.0.0")
    assert str(ComponentRef("router", "10.2.30")) == "router@10.2.30"
    assert str(TRIGGER) == "trigger@1.0.0" and str(OUTPUT) == "output@1.0.0"


@pytest.mark.parametrize(
    "text", ["llm-call", "llm-call@1.0", "LLM@1.0.0", "a@01.0.0", "a@1.0.0\n", "a@1.0.0@2", ""]
)
def test_malformed_component_references(text: str) -> None:
    with pytest.raises(ValueError, match="^Malformed component reference"):
        ComponentRef.parse(text)
