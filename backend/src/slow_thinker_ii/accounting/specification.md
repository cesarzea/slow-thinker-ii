# Accounting rules: specification

Defines exact monetary values, tariffs and budget admission independently of storage or provider clients.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- BudgetScope, ScopeKind and admit define admission against run, session and month scopes.
- Reservation, ScopeKeys and SettlementOutcome describe accounting decisions.
- parse_limit, rounded_charge and display_amount handle exact monetary boundaries.
- Tariff, TokenRates and TokenUsage calculate reservations and charges.

## Required behavior

- Use integer USD nanodollars internally and exact arithmetic for tariff calculations.
- Reject invalid limits and insufficient available budget without modifying state.
- Keep reservation, settled charge and unresolved exposure distinct; persistence owns atomic updates.

## Dependencies and ownership

Shared value contracts and the Python standard library; no provider SDK, HTTP or SQLite.

## Acceptance criteria

- Boundary equality, fractional rounding and all three budget scopes follow the accounting policy.
- Missing usage is not a zero-cost observation.

## Shared contracts

- [accounting-policy](../../../../docs/contracts/accounting-policy.md)
