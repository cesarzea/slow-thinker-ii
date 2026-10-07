# accounting: specification

Implements the arithmetic of the [accounting contract](../../../../docs/contracts/accounting.md).
Pure domain code; mutation testing (`mutmut`) covers this package.

## Public interface (`slow_thinker_ii.accounting`)

```python
QUANTA_PER_USD: int = 1_000_000_000            # one quantum is 10⁻⁹ USD
MAX_QUANTA: int = (1 << 63) - 1

def parse_usd(text: str) -> int                # exact; ValueError when not a decimal, negative,
                                               # over range or finer than 10⁻⁹
def format_usd(quanta: int) -> str             # "0.050000000"
def account_fraction(amount: Fraction) -> int  # USD → quanta, rounded up

@dataclass(frozen=True)
class Rates:                                   # USD per token
    input: Fraction
    cached_input: Fraction | None              # None: not billed
    cache_write: Fraction | None
    output: Fraction

@dataclass(frozen=True)
class Window:
    weekdays: frozenset[int]                   # ISO 1 = Monday … 7 = Sunday
    start_minute: int                          # minutes after 00:00 UTC
    end_minute: int                            # exclusive; greater than start_minute; at most 1440
    rates: Rates

@dataclass(frozen=True)
class Tariff:
    reviewed_on: str
    source: str
    rates: Rates
    long_context_above: int | None             # input tokens
    long_context: Rates | None
    windows: tuple[Window, ...]
    byte_bounded_input: bool                   # tokenizer encodes at least one byte per token
    input_capacity: int | None                 # required when byte_bounded_input is False

def parse_tariff(document: JsonValue, *, byte_bounded_input: bool = True,
                 input_capacity: int | None = None) -> Tariff

@dataclass(frozen=True)
class Usage:
    input: int                                 # uncached input tokens
    cached_input: int
    cache_write: int
    output: int

def input_bound(request_bytes: int, messages: int) -> int     # request_bytes + 16 * messages + 64
def reservation_bound(tariff: Tariff, input_tokens: int, output_tokens: int) -> int
def rates_at(tariff: Tariff, at: datetime, input_tokens: int) -> Rates
def charge(tariff: Tariff, usage: Usage, started: datetime, ended: datetime) -> tuple[int, Rates]

@dataclass(frozen=True)
class Scope:
    kind: Literal["run", "day", "month"]
    key: str
    limit: int
    used: int                                  # settled charges plus open reservations

def first_exhausted(scopes: Sequence[Scope], amount: int) -> Scope | None
def day_key(at: datetime) -> str               # "2026-10-04", UTC
def month_key(at: datetime) -> str             # "2026-10", UTC
```

## Behaviour

- `parse_usd`, `format_usd` and `account_fraction` keep the exact behaviour of the
  previous `parse_limit`, `display_amount` and `account_fraction`: amounts are exact,
  independent of the decimal context, and extreme exponents fail without expansion.
- `parse_tariff` reads the tariff document of the contract: decimal strings in USD per
  million tokens, converted exactly to `Fraction` per token. A rate is a plain
  non-negative decimal string of at most 9 integer digits and 18 decimals. `windows`
  and `long_context` are optional. Unknown or missing fields, values of the wrong type,
  empty `reviewed_on` or `source`, negative or malformed rates, a negative or
  non-integer `above_input_tokens`, malformed times (`HH:MM` from `00:00`, `end` up to
  `24:00`) or weekdays (a non-empty list of distinct ISO weekdays), a window that does
  not end after it starts, overlapping windows (sharing a weekday and minutes), and a
  missing or non-positive `input_capacity` raise `ValueError` naming the field.
- `rates_at` selects `long_context` when the reported input tokens (all categories)
  exceed `long_context_above`; otherwise the first window containing `at` (UTC weekday
  and minute, `end_minute` exclusive); otherwise `rates`.
- `charge` applies `rates_at` at `started` and at `ended`; when they differ, each
  category uses the higher rate (a billed rate is higher than an unbilled one). It
  returns the rounded-up quanta and the rates applied. Usage counts must be
  non-negative.
- `reservation_bound` multiplies the input bound by the highest input-category rate
  over every rate set and adds the output tokens times the highest output rate. When
  `byte_bounded_input` is False the input bound is `input_capacity`. `input_bound` and
  `reservation_bound` reject negative sizes.
- `first_exhausted` returns the first scope, in the given order, whose
  `used + amount > limit`.
- Every function that takes a `datetime` requires a timezone-aware value and raises
  `ValueError` otherwise; keys and windows use UTC.

## Acceptance

Tests cover the GPT-6 Luna and DeepSeek Flash tariffs of the step 1 configuration,
the long-context threshold, each DeepSeek window boundary, a call spanning a window
edge, rounding up, range errors, and every `parse_tariff` error. Mutation testing of
the package keeps at least the previous killed ratio (141 of 200).
