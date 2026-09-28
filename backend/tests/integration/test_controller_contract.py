"""The installed controller contract agrees with the documented component descriptor."""

from slow_thinker_host import decode_json, json_object
from slow_thinker_sequence import SequenceHost
from support.sequence_plans import EXAMPLES


def test_sequence_contract_matches_its_declared_type() -> None:
    manifest = json_object(decode_json((EXAMPLES / "sequence.component.json").read_text()))
    declared = json_object(json_object(manifest["operations"])["next"])
    operation = SequenceHost.describe({"steps": ["draft"]})[0]
    assert operation.name == "next"
    assert operation.input_schema == declared["input_schema"]
    assert operation.output_schema == declared["output_schema"]
