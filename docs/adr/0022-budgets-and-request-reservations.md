# ADR 0022: Run, daily and monthly budgets with request-size reservations

- Status: Proposed
- Recorded: 2026-10-04
- Decision-maker: Cesar Zea
- Requirements: CR12, CR13
- Amends: [ADR 0006](0006-execution-and-accounting.md) and the previous reservation policy

## Context and problem statement

The validated journeys use a run budget of USD 0.05. The previous policy reserved
the cost of a model's full published input capacity for every call; with the
recorded tariff fixtures one call reserved about USD 0.26, so such a budget could
not admit a single call. Budgets were scoped per run, saved work session and month;
the owner asked for run, day and month.

## Decision outcome

Before each model call the platform reserves an upper bound of its cost against the
run, the current UTC day and the current UTC month, atomically. The input bound is
the UTF-8 byte length of the request's messages and response format plus a fixed
per-message allowance, because each token of the supported providers' byte-level
tokenizers encodes at least one byte. The output bound is the call's maximum output
tokens. After the call the reservation is settled with the reported usage. When a
reservation is denied the run stops with the budget that was exhausted. Unknown
usage is settled at the reserved amount and marked as estimated. Money uses exact
integer quanta. See the [accounting contract](../contracts/accounting.md).

## Consequences

Budgets become usable at realistic values. The tokenizer assumption is recorded per
provider; a provider without it falls back to its published input capacity.
