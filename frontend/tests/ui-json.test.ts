import {expect, it} from 'vitest';
import {
  budgetShare,
  canonicalJson,
  isJsonObject,
  moneyLabel,
  readPointer,
  schemaAt,
  sumMoney,
  writePointer,
} from '../src/ui/index.ts';
import {declaration} from './support/contract.ts';

const config = {
  output_format: {type: 'json', schema: {type: 'object'}},
  'a/b': {'~c': 1},
  list: [1, 2],
};

it('reads values at JSON pointers, including escaped and array tokens', () => {
  expect(readPointer(config, '/output_format/type')).toBe('json');
  expect(readPointer(config, '/a~1b/~0c')).toBe(1);
  expect(readPointer(config, '/list/1')).toBe(2);
  expect(readPointer(config, '/list/x')).toBeUndefined();
  expect(readPointer(config, '/missing/deeper')).toBeUndefined();
  expect(readPointer(config, '')).toBe(config);
});

it('writes copies at JSON pointers, creating parents and removing undefined values', () => {
  const written = writePointer(config, '/output_format/schema', {type: 'array'});
  expect(written['output_format']).toEqual({type: 'json', schema: {type: 'array'}});
  expect(config.output_format.schema).toEqual({type: 'object'});
  expect(writePointer({}, '/a/b', 1)).toEqual({a: {b: 1}});
  expect(writePointer(config, '/output_format/schema', undefined)['output_format']).toEqual({
    type: 'json',
  });
  expect(writePointer(config, '', {replaced: true})).toEqual({replaced: true});
  expect(writePointer(config, '', 'not an object')).toBe(config);
});

it('finds the schema of a configuration value', () => {
  const schema = declaration('llm-call').config_schema;
  expect(schemaAt(schema, '/output_format/type')).toEqual({enum: ['text', 'json']});
  expect(schemaAt(declaration('router').config_schema, '/outputs/0')).toMatchObject({
    type: 'string',
  });
  expect(schemaAt(schema, '/prompt/deeper')).toBeUndefined();
  expect(schemaAt(schema, '/unknown')).toBeUndefined();
});

it('compares JSON values independently of key order', () => {
  expect(canonicalJson({b: [{d: 1, c: 2}], a: null})).toBe('{"a":null,"b":[{"c":2,"d":1}]}');
  expect(canonicalJson(undefined)).toBe('null');
  expect(isJsonObject([])).toBe(false);
  expect(isJsonObject({})).toBe(true);
});

it('formats money and budget shares', () => {
  expect(moneyLabel('0.000083')).toBe('$0.000083');
  expect(moneyLabel('1.00')).toBe('$1.00');
  expect(moneyLabel('20')).toBe('$20.00');
  expect(moneyLabel('0.500000000')).toBe('$0.50');
  expect(moneyLabel('n/a')).toBe('n/a');
  expect(moneyLabel('1.')).toBe('1.');
  expect(budgetShare('0.000083', '0.05')).toBe('0.2%');
  expect(budgetShare('0.00001', '0.05')).toBe('<0.1%');
  expect(budgetShare('0', '0.05')).toBe('0.0%');
  expect(budgetShare('1', '0')).toBe('—');
  expect(budgetShare('x', '1')).toBe('—');
  expect(sumMoney(['0.000031', '0.000033', '1', 'bad'])).toBe('1.000064000');
});
