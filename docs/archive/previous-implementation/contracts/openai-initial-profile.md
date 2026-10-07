# Initial OpenAI model profile

**Status: Approved first-cycle contract.** R08, R13–R14, R29; Q03–Q04, Q07–Q08. Live low-cost execution and retained costs are recorded in the [verification record](../verification.md); automated tests remain provider-free.

## Model selection

Use `gpt-6-luna` for the initial integration examples, with `reasoning_effort="none"`. This is a low-cost integration baseline, not a claim about the best model for later collaboration experiments. Keep the model in the resource profile, independently of agent code. The official model page lists Chat Completions support and the `none` setting. [Model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna).

Record both the requested model ID and returned model identity with each attempt. The documented ID is an alias; do not invent a dated snapshot or promise immutable model behavior. A future change of provider/model or reasoning effort creates a new recorded profile revision. Availability for the user's account remains unverified.

## Initial request boundary

| Item | Proposed behavior |
| --- | --- |
| Client | Ordinary synchronous/asynchronous Chat Completions client configured for the platform; provider credentials remain in the managed resource adapter. |
| Input/output | Text messages, one complete non-streamed response; LLMCall keeps its local text/JSON validation policy. |
| Generation settings | Explicit `reasoning_effort="none"`, `service_tier="default"` and a positive configured `max_completion_tokens`; no hidden SDK retries. |
| Provider persistence | Explicit `store=false`; this does not imply zero provider retention. |
| Extra options | Validate an allowlist before dispatch. Reject unimplemented tools, modalities, streaming, native schema modes and service tiers rather than silently ignore them. |
| Failures | Preserve provider details and available usage; distinguish incomplete output, refusal, bad request, unavailable model, rate/quota error, provider failure and uncertain transport outcome. |

The completion cap covers generated tokens that are not visible in the text as well. A local count of returned characters cannot replace reported usage. [Token-counting documentation](https://developers.openai.com/api/docs/guides/token-counting). Explicit Standard selection prevents an omitted tier from inheriting a different project setting; record the actual returned tier too. [Chat Completions reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create).

Propose Standard processing on the ordinary OpenAI endpoint, with both published context price bands in one tariff revision. Admission uses the conservative capacity bound below; settlement selects the actual band from reported input usage. Alternative tiers, regions and additional metered services require another complete profile. Tool-capable and memory-assisted components remain later extensions and may declare different request policies.

### Supported request subset

Propose string content with `system`, `developer`, `user` and `assistant` roles; preserve order and role without silently rewriting instructions. The provider recommends `developer` for newer models. The existing LLMCall specimen uses `system`; verify that exact recipe against the selected model before claiming support. Reject tool/function messages, multimodal parts, message names and extra message fields in this initial profile.

The caller supplies the bound model alias and messages through the normal SDK signature. The adapter resolves the alias to the frozen resource profile. Only `max_completion_tokens` may vary within its configured positive maximum; `reasoning_effort`, if supplied, must be `none`. Missing values use recorded profile defaults. The supported fixed wire values are `stream=false`, `n=1`, `store=false` and `service_tier="default"`; callers may supply those exact values, never alternatives. Reject every other generation option before dispatch. This restriction belongs to the initial adapter, not the generic component API.

In particular, reject `temperature`, `top_p`, stop sequences, tools, response formats, cache controls, metadata, predicted outputs and extra HTTP/body overrides until their behavior and accounting are supported. Do not silently remove a LangChain option. Its tested `max_tokens` constructor option serializes to `max_completion_tokens`; this does not establish native HTTP support for the legacy field. Endpoint, authentication, transport timeout and retry configuration remain host-owned. Both client-facing and provider-facing SDK clients use `max_retries=0`; an inner HTTP timeout must not exceed the remaining managed deadline.

### Response preservation and functional interpretation

The MCP model-resource proposal must carry the provider's complete parsed Chat Completions response under a `response` field, together with its provider request reference when available. The HTTP compatibility adapter returns that response in the native shape. Preserve identifiers, choices, finish reasons, refusal, actual model/tier, usage and unknown response fields within capture limits. Platform call IDs stay separate from provider IDs. Error handling and redaction must not expose provider authentication.

The model descriptor now uses a native `request` input envelope and a `response` or `error` output envelope. Installed discovery specializes the request schema to the admitted model alias and token limits; the resource preserves provider evidence in that envelope. The generic component contract still permits other resource-specific response shapes; it does not require every model provider to use OpenAI's format.

Provider HTTP success and usable LLMCall output are different decisions. A complete HTTP 200 response remains a native response for ordinary clients, even if it contains a refusal or reaches a token limit. LLMCall checks it before constructing its internal `ModelResponse` and invoking parsing/validation hooks. Apply the following checks in order; preserve all received evidence even when several conditions apply.

| Response condition | LLMCall interpretation |
| --- | --- |
| Malformed response, choice count other than one, or unexpected choice/message identity | `provider_response_invalid`; no successful binding. |
| Non-null refusal or `finish_reason="content_filter"` | `provider_refusal`; retain any returned text and refusal as evidence. |
| `finish_reason="length"` | `incomplete_response`, even if the partial text happens to parse as valid JSON. |
| Tool/function request or any other unsupported finish reason | `unsupported_response`; never execute an undeclared tool. |
| `finish_reason="stop"` but content is null or not a string | `missing_text`; do not substitute an empty string. |
| `finish_reason="stop"`, string content, no preceding failure | Continue normal text/JSON validation. An actual empty string is a text value; it fails JSON parsing in JSON mode. |

These proposed operation-failure codes are distinct from LLMCall's three completed-text validation codes. Usage settlement is independent of the outcome: refusal, incomplete output and invalid JSON can still cost money. Native clients retain their own documented interpretation; compatibility does not force them to adopt LLMCall's validation algorithm.

### HTTP errors and uncertain outcomes

For provider HTTP errors, preserve the status and bounded error body, including `type`, `code`, `param`, message and request reference when present. Native SDKs can then raise their normal status exceptions. Record error origin separately so provider authentication/quota errors are not confused with platform authority/budget denial. Unknown provider codes remain visible; do not parse human-readable messages to invent a more precise cause.

| Received condition | Recorded category / managed handling |
| --- | --- |
| Local schema, option, permission or budget rejection before dispatch authorization | Platform rejection; no external request and no billable dispatch. |
| Provider 400/422 | `provider_request_rejected`. |
| Provider 401/403 | `provider_access_denied`; credentials/access require operator review. |
| Provider 404 | `provider_not_found`; retain its code rather than assume a specific missing model. |
| Provider 429 with a documented credit, spending or usage-limit code | `provider_quota_denied`; distinct from an II budget denial. |
| Other provider 429 | `provider_rate_limited`; retain the code and any Retry-After evidence. |
| Provider 5xx | `provider_unavailable`; preserve overload/server details. |
| Other HTTP error | `provider_http_error`; keep status and body. |
| Timeout, connection loss or cancellation after possible dispatch | `provider_outcome_unknown`; retained obligation, no automatic replay. |

OpenAI documents several billing-related 429 codes and uses 503 for overload; classification therefore needs both status and structured error fields. [Error documentation](https://developers.openai.com/api/docs/guides/error-codes). The first profile performs no automatic retry for any row, including errors that could be retried later. A received HTTP error alone is not the selected accounting proof of zero charge; release requires the evidence policy in [accounting](accounting-policy.md#settlement-and-missing-evidence). Synthetic platform HTTP envelopes and their SDK exception mappings remain Q04/Q06; an upstream connection failure must not be presented as an actual provider HTTP response.

## Price evidence

Published GPT-6 Luna Standard rates, checked 2026-09-28, in **USD per 1,000,000 tokens**:

| Token category | Short context | Long context |
| --- | --- | --- |
| Input | 0.10 | 0.20 |
| Cached input | 0.01 | 0.02 |
| Cache writes | 0.125 | 0.25 |
| Output | 0.50 | 0.75 |

The model documentation places the long-context threshold above 272K input tokens. Regional processing and other service tiers can change rates. Save the applicable tariff revision and charge categories instead of treating all input tokens identically. [Model pricing](https://developers.openai.com/api/docs/models/gpt-6-luna), [pricing schedule](https://developers.openai.com/api/docs/pricing).

For illustration only, 1,000 ordinary uncached input tokens plus 1,000 output tokens cost USD 0.0006 at short-context Standard rates, excluding cache writes, regional adjustments and other charges. This is token arithmetic, not a measured request or a complete reservation bound.

Use the [accepted daily automatic tariff import](accounting-policy.md#tariffs-and-trustworthy-bounds), preserving a validated local revision for each run. Catalogue prices must match the direct OpenAI billing profile; a Gateway listing alone does not establish that match. Before strict-cap dispatch, establish a conservative bound for the actual token-counting, output-cap, cache and provider billing behavior; reject an unbounded request. Reconcile actual reported usage without duplicating nested-call charges. Missing categories remain unresolved, not zero. Tariff schema implementation and Q07 accounting decisions remain outstanding; published USD rates alone do not decide the application's currency.

### Usage categories and reservation calculation

For the selected text profile, let `P` be `usage.prompt_tokens`, `C` its `prompt_tokens_details.cached_tokens`, `W` its `prompt_tokens_details.cache_write_tokens`, and `O` be `usage.completion_tokens`. Cache categories partition the input: ordinary input is `P - C - W`, not `P`. Their rates are alternatives, not additive surcharges. [Cache accounting](https://developers.openai.com/api/docs/guides/prompt-caching). Preserve the full usage object; output subtotals such as reasoning are already part of `O` and must not be billed twice.

Require non-negative integer counts, `C + W <= P`, and consistent totals when supplied. Missing category fields do not mean zero without a documented profile-specific guarantee. Inconsistent or insufficient usage leaves the attempt unsettled; a valid model result can still be recorded while its reservation remains unavailable. A returned tier or model identity outside the saved billing profile likewise requires reconciliation, not invented rates.

With complete categories, the exact token charge is:

`((P - C - W) * input_rate + C * cached_rate + W * cache_write_rate + O * output_rate) / 1_000_000`

A reservation with a proven input bound can conservatively assume every input token incurs the largest applicable input rate:

`(input_upper_bound * max(input_rate, cached_rate, cache_write_rate) + max_completion_tokens * output_rate) / 1_000_000`

This formula alone does not establish `input_upper_bound` or the applicable rates. The documented exact-count endpoint accepts Responses inputs; its equivalence to a Chat Completions request has not been established. Local token estimates cannot silently authorize strict-cap dispatch. [Counting scope](https://developers.openai.com/api/docs/guides/token-counting).

### Proposed initial bound: published model capacity

Recommend a deliberately conservative first bound based on the model's published capacity. OpenAI describes a context window as the token ceiling of a request, including input and output; the selected model lists 1,050,000 context tokens and 128,000 maximum output tokens. These are provider specifications, not a measured billing guarantee. [Context definition](https://developers.openai.com/api/docs/guides/conversation-state#managing-the-context-window), [model limits](https://developers.openai.com/api/docs/models/gpt-6-luna).

For this text-only, single-response Standard profile, set `input_upper_bound = 1_050_000`; require a positive `max_completion_tokens <= 128_000`. For admission, use the highest input-category rate across both context bands (USD 0.25 per million) and the highest output rate (USD 0.75 per million). Do not assume a cache hit or short context. The resulting proposed reservation is:

`reservation_usd = (1_050_000 * 0.25 + max_completion_tokens * 0.75) / 1_000_000`

The bound intentionally does not subtract output capacity from input capacity. Under the documented token ceiling and saved tariff, every non-negative input category costs at most the chosen input rate and generated output stays within the enforced cap. This yields a conservative bound without an exact preflight token count or a second provider request. Payload/schema limits remain independently enforced; a budget reservation does not prove that the provider will accept a prompt.

| Illustrative output cap | Internal reservation, USD | Meaning |
| --- | --- | --- |
| 1 | 0.262500750 | Even a small output cap retains the full input allowance. |
| 2,048 | 0.264036000 | Illustration for a small experiment; not an approved default. |
| 128,000 | 0.358500000 | Largest output cap allowed by this proposed profile. |

For example, after a USD 0.264036000 reservation, complete usage of 1,000 ordinary short-context input tokens and 1,000 output tokens calculates to USD 0.000600000. Settlement replaces the reservation with that charge and releases USD 0.263436000. A response with unknown usage retains the reservation. These examples describe internal allowance, not an extra provider charge or a prediction of the request's cost.

The tradeoff is lower budget utilization: remaining allowance of USD 0.01 cannot authorize this profile even when a typical short call would cost much less. Show the required reservation and remaining allowance on denial. Never raise a configured cap automatically. Sequential settled calls reuse released allowance; simultaneous or unresolved attempts each consume their own reservation.

Freeze the model capacity, pricing bands, endpoint/tier constraints and bound-policy version with each admitted attempt. This recommendation assumes the provider honors its published capacity and billing categories. It does not establish what an out-of-contract provider charge could be, nor guarantee a final invoice ceiling. Reject unsupported metered options before dispatch; a returned usage/cost outside the saved bound triggers the existing excess-charge policy. Changes to model capacity or billing semantics require review; compatible numeric rate updates follow the accepted daily import policy for new runs.

Q04/Q07 approved this conservative strategy and its user-visible tradeoff. It is an alternative to requiring an exact Chat Completions input counter for the first cycle. A future tighter bound requires independent evidence and a new bound-policy revision; successful sample calls alone cannot justify reducing it. USD and UTC calendar months are approved; daily automatic tariff updates are accepted under Q03.

## Acceptance cases

CP06 must cover both normal clients and LLMCall: supported-role serialization; fixed tier/cap/retry values; unsupported fields rejected before external calls; each response/error row; no retry on 429, 5xx or connection failure; complete provider-response preservation through MCP and HTTP; and missing/overlapping cache categories. Exercise parseable JSON marked incomplete, empty string versus null, late usage, both pricing bands, all cache categories, capacity/rate mismatch and admission just below/at the reservation. Use deterministic provider fixtures and a separately authorized live smoke test for model/account support. Arithmetic checks and a successful model call cannot prove provider compliance with every pricing/capacity assumption.

## Verification boundary

Documentation establishes the candidate model, published rates and proposed request/response/error rules. Live access, response/error mapping, exact usage categories, cancellation behavior, pre-dispatch bounds and full client interoperability are not yet verified. The four graph fixtures still use illustrative profile references until the installation/limits/provider schemas are approved. The model-resource descriptor now includes the native result envelope described above. No SDK, credentials or executable provider configuration is installed by this document.
