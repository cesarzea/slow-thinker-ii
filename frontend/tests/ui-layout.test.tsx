import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {afterEach, beforeAll, expect, it, vi} from 'vitest';
import {cleanup, render, screen} from '@testing-library/react';
import type {GraphNode, UiSection} from '../src/api/index.ts';
import {SectionFields} from '../src/features/editor/dialogs/section-fields.tsx';
import {catalog, declaration} from './support/contract.ts';

/** Vitest leaves stylesheet imports empty, so this test applies the ui stylesheet itself. */
beforeAll(() => {
  const style = document.createElement('style');
  style.textContent = readFileSync(resolve(import.meta.dirname, '../src/ui/ui.css'), 'utf8');
  document.head.append(style);
  return () => {
    style.remove();
  };
});
afterEach(cleanup);

const css = (element: Element | null, property: string): string => {
  if (element === null) throw new Error(`No element to read ${property} from`);
  return getComputedStyle(element).getPropertyValue(property);
};

const SECTION: UiSection = {
  id: 'limits',
  title: 'Limits',
  columns: 2,
  fields: [
    {path: '/count', control: 'number', label: 'Count', label_position: 'start'},
    {path: '/notes', control: 'multiline', label: 'Notes'},
  ],
};

it('lays a two-column section out with full-width fields across and labels beside values', () => {
  const node: GraphNode = {id: 'n', name: 'N', component: 'llm-call@1.0.0', config: {count: 3}};
  const entry = {
    key: 'host:limits',
    section: SECTION,
    declaration: declaration('llm-call'),
    embedded: false,
    position: null,
  };
  render(<SectionFields entry={entry} node={node} catalog={catalog} onConfig={vi.fn()} />);
  const count = screen.getByRole('spinbutton', {name: 'Count'});
  expect(css(count.closest('.section-form'), 'grid-template-columns')).toBe(
    'repeat(2, minmax(0, 1fr))',
  );
  const notes = screen.getByRole('textbox', {name: 'Notes'}).closest('.config-field');
  expect([notes?.className, css(notes, 'grid-column')]).toEqual([
    'config-field field-multiline width-full align-start label-top',
    '1 / -1',
  ]);
  const field = count.closest('.config-field');
  expect(field?.className).toBe('config-field field-number width-sm align-end label-start');
  expect(css(count.closest('.control'), 'grid-template-columns')).toBe(
    'minmax(8rem, 12rem) minmax(0, 1fr)',
  );
  expect(css(count, 'text-align')).toBe('end');
});
