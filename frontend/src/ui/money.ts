/** Keep positive calculated costs visible at the ledger's nanodollar precision. */
export function moneyLabel(amount: string | null): string {
  if (amount === null) return 'Coste pendiente';
  if (!/^\d+(?:[.]\d{1,9})?$/.test(amount)) throw new Error('Importe inválido');
  const separator = amount.indexOf('.');
  if (separator < 0) return `USD ${amount}`;
  const integer = amount.slice(0, separator);
  const fraction = amount.slice(separator + 1);
  const decimal = fraction.replace(/0{1,9}$/, '');
  return decimal.length > 0 ? `USD ${integer}.${decimal}` : `USD ${integer}`;
}
