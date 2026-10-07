const AMOUNT = /^(\d+)(?:\.(\d+))?$/u;

/**
 * A spent USD amount with exactly three decimals, rounded half up with exact decimal
 * arithmetic: “$0.084” for “0.0835”. A nonzero amount below half a thousandth shows
 * “<$0.001”. Text that is not a non-negative decimal is returned unchanged.
 */
export function spentLabel(amount: string): string {
  const match = AMOUNT.exec(amount);
  if (match === null) return amount;
  const [, whole = '0', fraction = ''] = match;
  const kept = BigInt(whole) * 1000n + BigInt(fraction.slice(0, 3).padEnd(3, '0'));
  const thousandths = kept + ((fraction[3] ?? '0') >= '5' ? 1n : 0n);
  if (thousandths === 0n && /[1-9]/u.test(amount)) return '<$0.001';
  const decimals = (thousandths % 1000n).toString().padStart(3, '0');
  return `$${(thousandths / 1000n).toString()}.${decimals}`;
}
