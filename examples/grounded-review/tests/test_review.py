"""A real derived package exercises schema validation before cross-input checks."""

from pathlib import Path

import pytest
from example_grounded_review import GroundedReview
from slow_thinker_host import decode_json, json_object
from slow_thinker_llm_call import JsonObject, JsonValue, LLMCallConfig, parse_config
from support.openai_calls import ModelStub, completion

ROOT = Path(__file__).resolve().parents[3]


def settings() -> LLMCallConfig:
    path = ROOT / "docs/contracts/examples/grounded-review.instance.json"
    return parse_config(json_object(decode_json(path.read_text()))["config"])


async def test_unknown_source_retains_exact_text_without_repair() -> None:
    raw = ' {"summary":"Review","citations":["b","a"]}\n'
    stub = ModelStub(completion(raw))
    async with stub.client() as client:
        component = GroundedReview(settings(), client, "model")
        result = await component.generate(
            {"problem": "p", "proposal": "q", "available_sources": []}
        )
    assert result["status"] == "error"
    error = result["error"]
    assert error["code"] == "output_validation_failed"
    assert error["raw_output"] == raw
    assert error["issues"] == [{"path": "/citations", "message": "Unknown sources: a, b"}]
    assert len(stub.requests) == 1


async def test_valid_review_and_later_invocation_do_not_share_sources() -> None:
    stub = ModelStub(completion('{"summary":"Review","citations":["a"]}'))
    async with stub.client() as client:
        component = GroundedReview(settings(), client, "model")
        valid = await component.generate(
            {"problem": "p", "proposal": "q", "available_sources": ["a"]}
        )
        invalid = await component.generate(
            {"problem": "p", "proposal": "q", "available_sources": ["b"]}
        )
    assert valid == {
        "status": "ok",
        "format": "json",
        "value": {"summary": "Review", "citations": ["a"]},
    }
    assert invalid["status"] == "error"


async def test_common_schema_rejects_invalid_citations_before_the_hook() -> None:
    stub = ModelStub(completion('{"summary":"Review","citations":[7]}'))
    async with stub.client() as client:
        result = await GroundedReview(settings(), client, "model").generate(
            {"problem": "p", "proposal": "q", "available_sources": []}
        )
    assert result["status"] == "error" and result["error"]["code"] == "output_schema_mismatch"


@pytest.mark.parametrize(
    "value,arguments",
    [
        (7, {}),
        ({"citations": []}, {"available_sources": "invalid"}),
        ({"citations": [7]}, {"available_sources": []}),
    ],
)
async def test_violated_hook_invariants_fail_explicitly(
    value: JsonValue, arguments: JsonObject
) -> None:
    async with ModelStub(completion("unused")).client() as client:
        with pytest.raises(TypeError, match="validated"):
            GroundedReview(settings(), client, "model").validate_result(value, arguments)
