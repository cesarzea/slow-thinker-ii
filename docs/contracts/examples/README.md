# Initial example graphs

**Draft definitions for the first functional cycle. The application is not implemented.**

The first UI will offer these bundled examples for selection, visualization and execution. Editing tools and manual JSON upload follow later. Example selection does not replace graph validation or permission and budget checks.

| Definition | Agent sequence | What it exercises |
| --- | --- | --- |
| [Single agent](single-agent.graph.json) | Proposer | One activation, managed model access and the basic observation path. |
| [Handoff](handoff.graph.json) | Proposer → planner | A second agent receives the first agent's output and the original problem. |
| [Review cycle](review-cycle.graph.json) | Proposer → reviewer → proposer | Revision from explicit proposal and review inputs; two agent identities and three activations. |
| [Repeated review](repeated-review.graph.json) | Proposer → reviewer → proposer → reviewer → proposer | Two rounds with distinct node IDs; the second round uses the revised proposal. |

All four use the same [input example](problem.input.json), [LLMCall type](llm-call.component.json), [model resource](model.component.json) and [sequence controller](sequence.component.json). They use text output; successful values are available at `/value`. The last node supplies the final text for each example; intermediate results remain inspectable. These updated definitions have revision `example-2`.

Each graph uses stateless agents and explicit input bindings. The repeated review is a fixed sequence of five activations, with no implicit memory or dynamic loop. These examples establish functional coverage; more review rounds do not imply a better answer.

The [JSON configuration](llm-call-json.config.json) and [successful result](llm-call-json-success.result.json) exercise structured output separately. [Invalid JSON](llm-call-invalid-json.result.json) and [schema mismatch](llm-call-schema-error.result.json) illustrate retained-response failures without another LLM call.

[GroundedReview](grounded-review.md) is a separate code-inheritance specimen with a [descriptor](grounded-review.component.json), [configured instance](grounded-review.instance.json) and [trusted registration](grounded-review.registration.json). It adds validation that cited source IDs were supplied in the input. Its [reference failure](grounded-review-reference-error.result.json) demonstrates a domain validation error. This example does not turn the ordinary reviewer instances in the four graphs into distinct component types.

The provider, model and limits profile names are placeholders. Executing these definitions will require component implementations and approved installation, provider, tariff and limit configuration. Schema and semantic checks can be performed now without making LLM calls.
