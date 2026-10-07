# Provider-neutral model resources

| Document control | Value |
| --- | --- |
| Contract ID | CONTRACT-MODELS-001 |
| Owner | Cesar Zea |
| Date | 2026-10-02 |
| Status | Active S04 delivery specification; implementation/verification pending |

## Configuration and runtime boundary

A graph configures `model-provider` version `0.1.0` with
`{"provider_profile":"deepseek-flash","model":"deepseek-flash"}` and binds the
agent's declared model slot to that resource. Reviewed backend settings supply
provider, real model, response identities, credential reference, output limits,
billing profile and review expiry. Initial providers are OpenAI and DeepSeek.
Legacy `example.model-resource` and its OpenAI setup remain supported.

`ModelProviderHost` exposes `complete`, taking `{"request":{...}}` and returning
`{"response":native_response,...}` or the existing explicit provider failure
shape. The provider registry is private implementation; functional request
normalization and bounded transport have explicit public package interfaces.
Provider selection never changes the agent's normal `AsyncOpenAI`/LangChain call
signatures. All such calls target the platform gateway and the bound resource.
Native responses remain intact, including any `reasoning_content`; no fabricated
reasoning, silent provider fallback, automatic retry or implicit repair is allowed.

The common text, non-streaming Chat Completions profile accepts reviewed model,
messages, one completion and bounded output. OpenAI retains its reviewed `none`
reasoning profile. DeepSeek supports `none`, `low`, `high`, `max`; `none` maps to
native `thinking: {type: disabled}`, others to native thinking with the selected
`reasoning_effort`. Map `max_completion_tokens` to native DeepSeek `max_tokens`.
Temperature is accepted only where the selected mode supports it. Reject unknown
options, model mismatches, tools/streaming/multimodal requests outside this profile
before paid dispatch; never silently discard an option.

Trusted endpoints are the exact approved provider origins, or explicit loopback
fixtures. Secrets are launch-only and redacted from echoed responses. Graphs and
browser configuration cannot supply credentials, provider URLs or SDK retries.
Each call makes one bounded HTTP attempt and retains native response/headers,
returned model, usage and transport uncertainty through existing evidence rules.
The common resource also records UTC request-start and response-finish timestamps
for reviewed time-dependent billing; these are component-reported evidence.

## Tariff sources and immutable selection

OpenAI continues daily import from the
[Vercel catalogue](https://ai-gateway.vercel.sh/v1/models). Its existing reviewed
profile, immutable digest and failed-refresh behavior remain compatible.
The Vercel DeepSeek entry has provider-variable rates and is not a direct DeepSeek
billing profile. Fetch the [official direct pricing table](https://api-docs.deepseek.com/quick_start/pricing/)
daily for `deepseek-flash`. Bounded TLS parsing must validate model identity,
capacity, USD units, cache-hit/miss/output categories and the UTC schedule. A
changed or malformed unsupported structure fails without replacing valid prices.
Retain the captured source and a digest-bound normalized rate representation.

Review baseline on 2026-10-02: input capacity 1,000,000; output capacity 384,000.
Peak rates per million tokens: input miss 0.30, cache hit 0.006, output 1.20;
off-peak 0.15, 0.003, 0.60. Peak intervals are 01:00–04:00 and 06:00–10:00 UTC,
Monday–Friday. Cache creation has no additional separate surcharge in this profile.
These values are a reviewed baseline, not a permanent hardcoded price list.
Sources: [pricing](https://api-docs.deepseek.com/quick_start/pricing/),
[request/usage contract](https://api-docs.deepseek.com/api/create-chat-completion/).

Application public port `workspace.ModelTariffReader.selected(profile_id)` returns
`ModelTariffSelection(revision: TariffRevision, validated_at: int)` or `None`.
A legacy OpenAI reader remains usable. Per-profile refresh status and source
revisions are persisted separately; one failing source does not replace another.
Freeze each resource's selected revision in the prepared host and saved snapshot.
The existing global OpenAI tariff snapshot remains readable; new snapshots add
model-specific evidence per instance. Refreshing never recalculates old charges.

## Reservations and reconciliation

`ModelPricePolicy` uses the existing quote/reconcile port. DeepSeek always reserves
the maximum reviewed peak input/cache/output exposure at published capacity and
requested output cap. Do not infer cheapness from the visible prompt length.
Validate native prompt/completion/total/cache-hit/cache-miss counts and reviewed
response model identities; reasoning output is already included in completion
usage and must not be counted twice.

For time-dependent reconciliation, both reported transport timestamps must be
finite, ordered and in one uninterrupted billing interval. Verify that any native
`created` timestamp is consistent with the captured interval. If timing spans a
boundary or is missing/inconsistent, preserve the reservation as unresolved and
record the reason. When the interval is unambiguous, apply its exact normalized
rates with existing integer-quanta rounding. Verified usage and calculated charges
are not a provider invoice. Retain their source, timing and billing assumptions.
Missing or failed provider outcomes are not proof of a zero charge.

## Preparation and discovery handoff

Retain ResourceSettings version 1 and default old ProviderProfile fields to OpenAI.
Add explicit provider/billing-profile selection for new profiles. Preparation
exports `model_capabilities(settings) -> tuple[JsonObject, ...]`, with keys
`provider_profile`, `provider`, `model`, `reasoning_efforts`,
`supports_temperature`, `default_output_tokens`, `maximum_output_tokens`,
`billing_profile`, `review_expires_at`; no credential fields.

Add optional `model_tariffs: workspace.ModelTariffReader | None` to preparation
without breaking old positional callers. `HostRequest.runtime_id` identifies
run-owned resource state. `HostProfile.model_tariff` freezes the selected value.
Register host adapter `model-resource`; retain `openai-client`, `openai-resource`
and `plain`. The new resource's trusted effective host config includes provider,
actual/alias model, reviewed reasoning modes and output bounds. A mismatched or
stale profile fails before graph launch.

Acceptance and ownership are in [the delivery block](../specification/s04-s06-delivery.md).

## Reviewed public-holiday calendar

The pricing footnote excludes Chinese public holidays from peak periods. The
[State Council 2026 notice](https://www.gov.cn/zhengce/zhengceku/202511/content_7047091.htm)
provides the reviewed 2026 calendar: January 1–3, February 15–23, April 4–6,
May 1–5, June 19–21, September 25–27 and October 1–7 (Asia/Shanghai dates).
Capture the calendar year, source and ranges with normalized tariff evidence.
The published Monday–Friday rule keeps weekend makeup working days off-peak.
Outside a reviewed calendar year, possible peak weekday periods remain unresolved;
weekends and hours outside both peak windows can still be priced off-peak.
Reservations always retain the maximum peak bound. Calendar policy is separately
reviewed; automatic daily refresh updates rates without inventing holiday dates.

The reviewed DeepSeek text subset accepts system/user/assistant message roles.
Developer and tool roles are unsupported and fail before paid dispatch. Existing
OpenAI developer-role support remains unchanged; normalization never discards a role.
