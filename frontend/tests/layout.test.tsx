import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {afterEach, beforeAll, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, within} from '@testing-library/react';
import {editorApi, renderEditor, settled} from './support/editor-harness.tsx';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {j1, j3} from './support/contract.ts';

/** Vitest leaves stylesheet imports empty, so these tests apply the module stylesheets themselves. */
beforeAll(() => {
  const style = document.createElement('style');
  style.textContent = ['features/editor/editor.css', 'ui/ui.css']
    .map((path) => readFileSync(resolve(import.meta.dirname, '../src', path), 'utf8'))
    .join('\n');
  document.head.append(style);
  return () => {
    style.remove();
  };
});
beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.unstubAllGlobals();
});

/** A declared value of an element's computed style: jsdom applies the cascade, not the layout. */
function css(element: Element | null, property: string): string {
  if (element === null) throw new Error(`No element to read ${property} from`);
  return getComputedStyle(element).getPropertyValue(property);
}

/** The grid rows of the editor and of its header, body and status bar. */
function editorRows(): Record<string, string> {
  const body = screen.getByRole('complementary', {name: 'Graph'}).parentElement;
  return {
    editor: css(body?.parentElement ?? null, 'grid-template-rows'),
    header: css(screen.getByRole('heading', {level: 1}).closest('header'), 'grid-row'),
    body: css(body, 'grid-row'),
    status: css(screen.getByText('No problems').closest('footer'), 'grid-row'),
  };
}

it('keeps the editor body in the row that takes the remaining height', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  await settled();
  expect(editorRows()).toEqual({
    editor: '52px minmax(0, 1fr) 28px',
    header: '1',
    body: '2',
    status: '3',
  });
});

it('lets the editor palette and side panel scroll on their own', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  const panel = screen.getByRole('complementary', {name: 'Graph'});
  const palette = screen.getByRole('navigation', {name: 'Components'});
  expect(css(panel.parentElement, 'grid-template-rows')).toBe('minmax(0, 1fr)');
  expect([palette, panel].map((part) => [css(part, 'overflow'), css(part, 'min-height')])).toEqual([
    ['auto', '0px'],
    ['hidden auto', '0px'],
  ]);
});

it('keeps the node dialog at one size and place, whichever section it shows', async () => {
  await renderEditor(editorApi('funny-story-with-review', j3), 'funny-story-with-review');
  fireEvent.click(screen.getByRole('group', {name: 'Reviewer'}));
  fireEvent.click(screen.getByRole('button', {name: 'Edit Prompt'}));
  const dialog = screen.getByRole('dialog', {name: 'Reviewer'});
  const frame = (): string[] => [
    css(dialog.parentElement, 'align-items'),
    css(dialog.parentElement, 'padding-top'),
    css(dialog, 'width'),
    css(dialog, 'height'),
    css(dialog, 'overflow'),
  ];
  const before = frame();
  // jsdom resolves 6vh, and min(960px, 100vw - 2rem) in its 1024px-wide window.
  expect(before).toEqual([
    'flex-start',
    `${String(window.innerHeight * 0.06)}px`,
    '960px',
    expect.stringMatching(/^min\(680px, 100dvh - (?:4rem|64px)\)$/u),
    'hidden',
  ]);
  const list = within(dialog).getByRole('tablist', {name: 'Sections'});
  fireEvent.click(within(list).getByRole('tab', {name: 'Script'}));
  expect(frame()).toEqual(before);
  const panel = within(dialog).getByRole('tabpanel', {name: 'Script'});
  expect([list, panel].map((part) => [css(part, 'overflow'), css(part, 'min-height')])).toEqual([
    ['auto', '0px'],
    ['auto', '0px'],
  ]);
});
