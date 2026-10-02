# Tariff catalog import: specification

Fetches and validates the Vercel model catalog into immutable local tariff revisions.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- VercelTariffSource implements TariffSource.fetch.
- parse_catalog validates downloaded catalog content into a TariffRevision.
- SOURCE_URL identifies the external catalog source.

## Required behavior

- Validate supported billing categories, capacities, currency and rates before publishing a revision.
- A failed fetch or invalid catalog must not replace the last valid revision.
- This adapter supplies pricing data only; the application service schedules daily refresh.

## Dependencies and ownership

HTTP transport and public accounting/application tariff contracts.

## Acceptance criteria

- Malformed or unsupported billing data is rejected explicitly.
- Running and historical attempts retain their frozen tariff revisions after refresh.

## Shared contracts

- [accounting-policy](../../../../../docs/contracts/accounting-policy.md)
- [openai-initial-profile](../../../../../docs/contracts/openai-initial-profile.md)

## S04–S06 active delivery

Follow [the shared contract](../../../../../docs/contracts/model-resources.md). Implementation owner: A.

Retain VercelTariffSource/parse_catalog behavior. Add public DeepSeekTariffSource and strict bounded official HTML-table parsing with digest-bound normalized peak/off-peak rates, schedule and captured source. Unknown/model-variable Vercel prices must not become direct DeepSeek tariffs. Use existing TariffSource API; coordinator owns scoped SQLite stores and refresh composition.

Completion requires the shared delivery acceptance evidence; implementation alone
does not close verification. Keep existing approved contracts compatible.

## S04–S06 development implementation

The public entry point adds `DeepSeekTariffSource`, `parse_deepseek_pricing`,
`DEEPSEEK_SOURCE_URL`, `DEEPSEEK_PROFILE_ID` and `deepseek_schedule`; existing
Vercel interfaces remain unchanged. The direct source makes one bounded TLS
fetch, disables redirects/proxy inheritance, requires HTML and limits decoded
capture to 256 KiB. The application owns independent daily scheduling/storage.

The parser handles the official table's merged cells without executing page
content. It bounds nodes, rows, columns and spans, rejects holes/collisions, and
validates exact Flash identity, capacities, USD categories, peak/off-peak relation
and published schedule including holiday exclusion. Unsupported source changes
raise a validation failure; existing refresh handling retains the last valid
revision. Vercel DeepSeek entries never supply direct DeepSeek prices.

Immutable `source_json` is canonical JSON containing captured HTML and normalized
rates/schedule/calendar, with a digest over that whole representation. Domain
short/long context rates both retain the peak baseline; off-peak rates live in
normalized source evidence. The separately reviewed 2026 calendar is included
through `deepseek_schedule`; daily import does not invent later holiday dates.

This implements the source half of A05–A06. Sample-table, malformed-source,
failed-refresh retention and independent scheduling verification remain pending
until the assigned M06 testing phase.

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

## HTML parser callback verification

PricingTable.handle_starttag and handle_endtag override the standard HTMLParser
callbacks invoked by feed; typing.override checks their inherited signatures.
Vulture's static unused-method findings for these two callbacks are framework
dispatch false positives. Public parse_deepseek_pricing regressions execute both
through feed, including merged cells, malformed nesting, missing closing tags,
unsupported additional tables and structural bounds. The HTML extraction helper
has 100% line and branch coverage. This evidence applies only to these callbacks;
it does not justify a general dead-code exclusion.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
