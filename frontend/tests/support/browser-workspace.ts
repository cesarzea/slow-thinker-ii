import {Buffer} from 'node:buffer';
import {readFile} from 'node:fs/promises';
import {expect} from '@playwright/test';
import type {Page} from '@playwright/test';
import {editor, openSource} from './browser-authoring.ts';
export async function workspacePage(page: Page, name: string): Promise<void> {
  await page
    .getByRole('navigation', {name: 'Workspace'})
    .getByRole('button', {name, exact: true})
    .click();
}
export async function importCollaboration(page: Page): Promise<void> {
  const canonical = await readFile(
    new URL('../../../docs/contracts/examples/resource-collaboration.graph.json', import.meta.url),
    'utf8',
  );
  const source = canonical
    .replace('"limits_profile": "illustrative-limits"', '"limits_profile": "browser"')
    .replace('"graph_id": "resource-collaboration"', '"graph_id": "browser-collaboration"')
    .replace(
      '"max_completion_tokens": 1024',
      '"max_completion_tokens": 1024,"temperature":1.0,"seed":9007199254740993',
    );
  await openSource(page);
  await page.getByLabel('Import UTF-8 JSON file').setInputFiles({
    name: 'collaboration.json',
    mimeType: 'application/json',
    buffer: Buffer.from(source),
  });
  await expect(editor(page)).toHaveValue(source);
}
export async function applyField(page: Page, label: string, value: string): Promise<void> {
  await page.getByRole('textbox', {name: label, exact: true}).fill(value);
  await page.getByRole('button', {name: `Apply ${label}`, exact: true}).click();
  await expect(page.getByText('Applying form change…', {exact: true})).toHaveCount(0);
}
export async function runCollaboration(page: Page): Promise<void> {
  await workspacePage(page, 'Runs');
  await page.getByLabel('Task or problem').fill('Compare an exact calculation');
  await page.getByRole('textbox', {name: 'expression (required)', exact: true}).fill('2+3');
  await page.getByRole('button', {name: 'Start run', exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Completed', exact: true})).toBeVisible();
  await expect(page.getByRole('region', {name: 'Final result'})).toContainText('Test result');
}
export async function collaborationCanvas(page: Page): Promise<void> {
  await workspacePage(page, 'Runs');
  const live = page.getByRole('region', {name: 'Selected run graph'});
  await expect(live).toContainText('Saved definition: browser-collaboration · example-1');
  const canvas = live.getByLabel('Agent collaboration canvas');
  await expect(canvas).toBeVisible();
  for (const id of ['draft', 'review']) {
    const node = canvas.locator(`.react-flow__node[data-id="node:${id}"]`);
    await expect(node).toBeVisible();
    await expect(node).toContainText('completed · 1 recorded activation');
  }
  await expect(live.getByRole('status')).toHaveCount(0);
}

export async function expectWorkspaceFits(page: Page): Promise<void> {
  const size = await page.evaluate(() => ({
    viewport: innerWidth,
    document: document.documentElement.scrollWidth,
    overflow: [...document.querySelectorAll('main *')]
      .filter((item) => item.getBoundingClientRect().right > innerWidth)
      .slice(0, 8)
      .map((item) => ({tag: item.tagName, right: item.getBoundingClientRect().right})),
  }));
  expect(size.document, JSON.stringify(size.overflow)).toBeLessThanOrEqual(size.viewport);
}
