# Reviewed model policies: specification

Follow the [shared contract](../../../../../docs/contracts/model-resources.md) and
[delivery acceptance matrix](../../../../../docs/specification/s04-s06-delivery.md).
Implementation owner: A.

## Public boundary and dependencies

The [public entry point](__init__.py) exports immutable `ModelProfile` and
`ModelPricePolicy`. Inputs are public `TariffRevision`, alias/output bounds,
reviewed returned-model identities, JSON operation arguments and `OperationResult`.
Outputs are existing application `ChargeBasis` and `ChargeEvidence` values.
Dependencies are public accounting/application/contracts APIs, the legacy OpenAI
policy and the tariff adapter's reviewed schedule policy. No provider I/O occurs.

## Implemented behavior and state

The provider registry binds actual model and billing profile independently of the
settings dictionary key. Every policy owns a frozen revision. OpenAI delegates
unchanged to `OpenAIProfile`/`OpenAIPricePolicy`; DeepSeek validates the native
text subset and reasoning options before quote/dispatch. Developer/tool messages
and unsupported options are rejected explicitly.

DeepSeek quote reserves reviewed peak input capacity plus the requested output
cap. The normalized direct source, digest and request options remain in the quote.
Both domain context bands remain peak rates; temporal selection does not alter
`Tariff` semantics. Reconciliation verifies returned model, nonnegative integer
usage, cache-hit plus cache-miss partition, total usage and published capacities.
Reasoning output is already part of completion usage and is never added twice.

Transport start/finish must be finite, ordered and within one actual billing
interval. Native integer `created`, if supplied, may use whole-second resolution
and must lie between the capture's floor(start) and floor(finish). Reviewed calendar
exclusions mask peak windows; future possible peak weekdays remain unresolved.
An interval exceeding fourteen days is conservatively unresolved and bounds
calendar traversal. Actual rate changes, rather than masked schedule boundaries,
prevent settlement. Verified amounts use existing exact rational/quanta rounding.
Missing outcomes, malformed usage or inconsistent timing produce unavailable
charge evidence with fixed reasons and retain reservation exposure.

The direct source digest, normalized identities/rates and reviewed schedule are
validated before policy creation. Daily refresh cannot mutate an existing policy
or historical charge.

## Acceptance and verification

A03 uses pure request validation; A05–A06 use immutable direct source validation,
peak reservations and usage/timing reconciliation. A07 delegates legacy behavior.
Request/usage/cache/timing/calendar/rounding and integration verification remains
pending until the assigned M06 testing phase; development static checks alone do
not establish acceptance.

## S04–S06 scoped testing evidence

The assigned A acceptance/regression suite passes 532 tests using recorded official
prices, isolated SQLite state and simulated native provider transport. Ordinary
OpenAI SDK, LangChain and unchanged LLMCall requests cross actual loopback gateway,
managed authority, real model host/transport and pricing boundaries. Separate
caller grants select independent providers; cross-agent binding requests fail
before native dispatch. Exact cache/timing/calendar charges, source retention,
quanta rounding and historical quote/snapshot preservation pass.

Preparation evidence uses production InstalledWorkflowPreparer with explicitly
description-only installations; it does not claim installed inference. No paid
provider calls occurred. Scoped static checks pass. Coordinator review and full
unchanged verification remain pending; the complete S04–S06 delivery is not yet
claimed verified.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
