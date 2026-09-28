"""Component contracts are pure configuration operations and preserve subclass inheritance."""

import pytest
from example_grounded_review import GroundedReview
from slow_thinker_host import JsonObject, json_object
from slow_thinker_llm_call import LLMCall
from slow_thinker_openai_model import OpenAIModelHost
from support.openai_calls import config


def test_inherited_agent_describes_configured_input_without_a_model_client() -> None:
    settings = json_object(config())
    first = LLMCall.describe(settings)
    assert GroundedReview.describe(settings) == first
    first[0].input_schema["changed"] = True
    assert "changed" not in LLMCall.describe(settings)[0].input_schema


def test_model_resource_can_describe_without_a_provider_credential() -> None:
    settings: JsonObject = {
        "model_alias": "bound",
        "model": "actual",
        "default_output_tokens": 8,
        "maximum_output_tokens": 32,
    }
    assert OpenAIModelHost.describe(settings)[0].name == "complete"
    with pytest.raises(ValueError):
        OpenAIModelHost.describe({})
