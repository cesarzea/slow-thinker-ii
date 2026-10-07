const DIGITS = /^\d+$/u;

/** Split a non-negative decimal string into its whole and fractional digits. */
function decimalParts(amount: string): [string, string] | null {
  const [whole = '', fraction = '', ...rest] = amount.split('.');
  const valid =
    DIGITS.test(whole) && (fraction === '' || DIGITS.test(fraction)) && rest.length === 0;
  return valid && !amount.endsWith('.') ? [whole, fraction] : null;
}

/** Show a decimal USD amount with at least two decimals and no trailing zeros beyond them. */
export function moneyLabel(amount: string): string {
  const parts = decimalParts(amount);
  if (parts === null) return amount;
  return `$${parts[0]}.${withoutTrailingZeros(parts[1]).padEnd(2, '0')}`;
}

function withoutTrailingZeros(digits: string): string {
  let end = digits.length;
  while (end > 0 && digits[end - 1] === '0') end -= 1;
  return digits.slice(0, end);
}

/** Show how much of a budget an amount uses, as a percentage. */
export function budgetShare(amount: string, budget: string): string {
  const spent = Number(amount);
  const limit = Number(budget);
  if (Number.isNaN(limit) || limit <= 0 || !Number.isFinite(spent)) return '—';
  const share = (spent / limit) * 100;
  if (share > 0 && share < 0.1) return '<0.1%';
  return `${share.toFixed(1)}%`;
}

/** Add decimal USD amounts exactly, in nano-dollars. */
export function sumMoney(amounts: readonly string[]): string {
  const nanos = amounts.reduce((total, amount) => total + toNanos(amount), 0n);
  const whole = nanos / 1_000_000_000n;
  const fraction = (nanos % 1_000_000_000n).toString().padStart(9, '0');
  return `${whole.toString()}.${fraction}`;
}

function toNanos(amount: string): bigint {
  const parts = decimalParts(amount);
  if (parts === null) return 0n;
  return BigInt(parts[0]) * 1_000_000_000n + BigInt(parts[1].slice(0, 9).padEnd(9, '0'));
}
