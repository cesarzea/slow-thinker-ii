"""A real model resource host receives only its own explicit synthetic provider credential."""

import sys
from pathlib import Path

from slow_thinker_host import JsonObject, Operation, encode_json
from slow_thinker_ii.adapters.process import ComponentProcess, ProcessLaunch, ProcessSecret
from slow_thinker_ii.contracts import OperationContract
from slow_thinker_openai_model import ModelConfig, effective_operation

SECRET = "fixture-provider-key"


def bootstrap_record(config: ModelConfig, operation: Operation, port: int) -> JsonObject:
    return {
        "config": {
            "model_alias": config.model_alias,
            "model": config.model,
            "default_output_tokens": 8,
            "maximum_output_tokens": 32,
        },
        "operations": [
            {
                "name": operation.name,
                "input_schema": operation.input_schema,
                "output_schema": operation.output_schema,
            }
        ],
        "clients": {
            "provider": {
                "base_url": f"http://127.0.0.1:{port}/v1",
                "timeout_seconds": 5,
                "close_seconds": 1,
                "max_response_bytes": 524_288,
            }
        },
    }


def provider_process(directory: Path, port: int) -> ComponentProcess:
    config = ModelConfig("bound-model", "gpt-6-luna", 8, 32)
    operation = effective_operation(config)
    record = bootstrap_record(config, operation, port)
    bootstrap = directory / "provider.json"
    bootstrap.write_text(encode_json(record))
    launch = ProcessLaunch(
        Path(sys.executable),
        "slow_thinker_openai_model",
        bootstrap,
        directory,
        5,
        3,
        1_048_576,
        (ProcessSecret("SLOW_THINKER_SECRET_OPENAI", SECRET),),
    )
    contract = OperationContract(
        operation.name, encode_json(operation.input_schema), encode_json(operation.output_schema)
    )
    return ComponentProcess(launch, (contract,))
