import {expect, it, vi} from 'vitest';
import {sourceTree, sourceString, pointerToken} from '../src/ui/index.ts';
import {resolveSchema, schemaObject} from '../src/features/workspace/schema-resolution.ts';
it('preserves raw scalar literals, escaped keys and empty nested values', () => {
  const root = sourceTree(
    ' {"large":9007199254740993,"float":1.0,"a\\"b":[{},[],"x\\"y", true, null]} ',
  );
  if (root === null) throw new Error('Expected readable JSON');
  const nested = root.entries.get('a"b');
  if (nested === undefined) throw new Error('Expected escaped key');
  expect(root.entries.get('large')?.raw).toBe('9007199254740993');
  expect(root.entries.get('float')?.raw).toBe('1.0');
  expect(nested.items.map((item) => item.raw)).toEqual(['{}', '[]', '"x\\"y"', 'true', 'null']);
  expect(sourceString(nested.items[2])).toBe('x"y');
  expect(pointerToken('a~/b')).toBe('a~0~1b');
});
it.each(['{', '[', '', '['.repeat(66) + '0' + ']'.repeat(66)])(
  'rejects invalid or overly nested previews',
  (source) => {
    expect(sourceTree(source)).toBeNull();
  },
);
it('treats missing/non-string/malformed fields as unavailable text', () => {
  expect(sourceString(undefined)).toBe('');
  expect(sourceString(sourceTree('2') ?? undefined)).toBe('');
  expect(sourceString({raw: '{', entries: new Map(), items: []})).toBe('');
});
it('resolves trusted URNs, allOf and escaped local fragments without network access', () => {
  const fetcher = vi.spyOn(globalThis, 'fetch');
  const document = {
    $defs: {'a/b': {type: 'object', properties: {flag: {type: 'boolean'}}}},
    allOf: [{$ref: '#/$defs/a~1b'}, {properties: {prompt: {type: 'string'}}}],
  };
  const result = resolveSchema({$ref: 'urn:external'}, {'urn:external': document});
  expect(schemaObject(result['properties'])).toMatchObject({
    flag: {type: 'boolean'},
    prompt: {type: 'string'},
  });
  expect(fetcher).not.toHaveBeenCalled();
  fetcher.mockRestore();
});
it.each(['https://unknown.invalid/schema', 'urn:missing', 'urn:test#bad'])(
  'retains unresolved schema constructs for JSON editing: %s',
  ($ref) => {
    expect(resolveSchema({$ref}, {'urn:test': {}})['properties']).toEqual({});
  },
);
it('bounds cyclic and excessive schema references', () => {
  const document = {$ref: 'urn:loop', properties: {next: {$ref: 'urn:loop'}}};
  expect(resolveSchema({$ref: 'urn:loop'}, {'urn:loop': document})).toBeTruthy();
  expect(resolveSchema({properties: {x: true}}, {}, {}, 21)).toEqual({});
  expect(resolveSchema({properties: {x: true}}, {}, {}, 0, {remaining: 0})).toEqual({});
  expect(schemaObject(null)).toEqual({});
});
