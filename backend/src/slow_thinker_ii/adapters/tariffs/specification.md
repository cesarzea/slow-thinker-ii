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
