import {describe, expect, it} from 'vitest';
import {moneyLabel} from '../src/ui/index.ts';

describe('cost labels', () => {
  it.each([
    [null, 'Cost pending'],
    ['0', 'USD 0'],
    ['0.000000001', 'USD 0.000000001'],
    ['12.010000000', 'USD 12.01'],
    ['0.000000000', 'USD 0'],
  ])('retains the meaning of %s', (amount, expected) => {
    expect(moneyLabel(amount)).toBe(expected);
  });
  it.each(['NaN', '-1', '0.0000000001', 'USD 1'])('rejects %s', (amount) => {
    expect(() => moneyLabel(amount)).toThrow('Invalid amount');
  });
});
