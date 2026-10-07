# Accounting and budgets

| Contract control | Value                                                                 |
| ---------------- | --------------------------------------------------------------------- |
| Contract ID      | CORE-ACCOUNTING-1                                                     |
| Decisions        | [ADR 0022](../adr/0022-budgets-and-request-reservations.md)           |
| Journeys         | V09, J3                                                               |

## Money

Amounts are United States dollars held as integers of 10⁻⁹ USD (nano-dollars).
Decimal strings with at most nine decimal places are the external form. Rates are
USD per million tokens. Every computed charge rounds up to the next nano-dollar.

## Budgets

| Scope   | Limit source                                             | Key              |
| ------- | -------------------------------------------------------- | ---------------- |
| `run`   | The graph's `limits.budget_usd`                           | Run identifier   |
| `day`   | Server configuration `budgets.daily_usd`                 | UTC date         |
| `month` | Server configuration `budgets.monthly_usd`               | UTC month        |

The used amount of a scope is the sum of its settled charges and open reservations.
A reservation is admitted only if, for every scope, the used amount plus the
reservation does not exceed the limit. Admission of all three scopes is one atomic
transaction. A denial names the first exhausted scope in the order run, day, month.

## Tariffs

Each model's tariff is reviewed configuration:

```json
{
  "reviewed_on": "2026-09-28",
  "source": "https://developers.openai.com/api/docs/pricing",
  "rates": {"input": "0.10", "cached_input": "0.01", "cache_write": "0.125", "output": "0.50"},
  "long_context": {"above_input_tokens": 272000,
                   "rates": {"input": "0.20", "cached_input": "0.02", "cache_write": "0.25", "output": "0.75"}},
  "windows": [
    {"weekdays": [1, 2, 3, 4, 5], "start": "01:00", "end": "04:00",
     "rates": {"input": "0.30", "cached_input": "0.006", "output": "1.20"}}
  ]
}
```

`rates` apply by default. `long_context`, optional, replaces them when reported
input tokens exceed its threshold. `windows`, optional, replace them during the
listed UTC weekday intervals (Monday is 1). A missing category rate means that
category is not billed by the provider. Holidays are not modelled; a provider
discount on holidays is therefore not applied.

The S06 configuration contains the reviewed OpenAI GPT-6 Luna rates of
2026-09-28 and the DeepSeek Flash rates of 2026-10-02 from the previous record.
Automatic daily tariff import is deferred.

## Reservation bound

For one model call:

- Input bound: the UTF-8 byte length of the serialized `messages` and
  `response_format`, plus 16 per message, plus 64.
- Output bound: the request's `max_completion_tokens`.
- Bound: input bound × the highest input-category rate in the tariff, plus output
  bound × the highest output rate, over default, long-context and window rates.

The input bound relies on byte-level tokenization, in which every token encodes at
least one byte; both S06 providers use it. A provider configured without that
property uses its reviewed input capacity instead.

## Settlement

The charge uses the reported token categories and the rates in force at the call's
start, or the higher rate per category if the call ended under different rates.
The reservation is replaced by the charge. When usage is unknown, the charge equals
the reservation and is marked estimated. A charge above its reservation is recorded;
if any scope is then exceeded, the run stops with that scope.

## Visibility

Each recorded model call contains the reserved amount, the charge, whether it is
estimated and the rates applied. The operator API reports the day's and month's
used amounts against their limits.
