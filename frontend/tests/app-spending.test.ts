import {expect, it} from 'vitest';
import {spentLabel} from '../src/app/spending.ts';

it.each([
  ['0', '$0.000'],
  ['0.000000000', '$0.000'],
  ['12', '$12.000'],
  ['0.5', '$0.500'],
  ['0.083', '$0.083'],
  ['0.0834999', '$0.083'],
  ['0.0835', '$0.084'],
  ['0.0005', '$0.001'],
  ['0.9995', '$1.000'],
  ['9.9995', '$10.000'],
  ['123456789012345678.123456789', '$123456789012345678.123'],
])('shows %s spent as %s', (amount, label) => {
  expect(spentLabel(amount)).toBe(label);
});

it.each(['0.000132200', '0.0004999', '0.000000001'])(
  'shows the nonzero amount %s that rounds to zero as <$0.001',
  (amount) => {
    expect(spentLabel(amount)).toBe('<$0.001');
  },
);

it.each(['-0.5', '1.', '.5', 'abc', ''])('returns the malformed amount %j unchanged', (amount) => {
  expect(spentLabel(amount)).toBe(amount);
});
