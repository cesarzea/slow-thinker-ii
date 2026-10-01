# Bounded proposer/reviewer collaboration

[bounded-review.graph.json](bounded-review.graph.json) is the bundled conditional
example. Its [input fixture](bounded-review.input.json) asks for a backup procedure
with seven explicit requirements. The first proposal is deliberately constrained
to a short draft. The reviewer accepts only when every requirement is satisfied;
on rejection it returns concrete findings for the next proposal. Model responses
are nondeterministic: the prompts do not guarantee rejection on the first pass.

The proposer and `review-worker` are ordinary, independently configured LLMCall
instances. Their model resource bindings, instructions and generation parameters
are separate. `reviewer` is a RoutedCall composition: it calls the worker's
`generate`, preserves the complete response, extracts `/value`, and calls the
Redirector. The deterministic `example_grounded_review:choose` selector returns
`accept` or `revise` from the validated `accepted` boolean. This uses no custom
reviewer reasoning or citation-validation subclass.

The graph marks the worker and redirector as `contained_by: reviewer`; containment
changes presentation only. Four explicit permission edges authorize all nested
calls. The model resources remain independently visible and configurable.

The `propose` activation receives the original problem, its last proposal and the
latest reviewer findings. On its first activation the latter two arguments are
omitted. Every subsequent binding names `latest_completed`, so evidence can retain
the exact prior activation selected. `accept` finishes with the latest proposal;
`revise` returns to the proposer. Six configured node activations allow at most
three proposal/review rounds. Acceptance on activation six succeeds; another
revision exhausts the controller without claiming acceptance.

Prepare with `python -m tooling.components --component all`. The default Redirector
recipe builds and hashes the example selector wheel alongside its dependencies;
installed invocation arguments never select source files or import references.
The illustrative model configuration is resolved by the local application's
explicit provider setup, as in the existing bundled examples. Functional and installed acceptance results are recorded in the
[verification record](../../verification.md).
