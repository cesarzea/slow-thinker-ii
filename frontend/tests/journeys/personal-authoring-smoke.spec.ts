import {expect, test} from '@playwright/test';
import type {Locator, Page} from '@playwright/test';
import {connect} from '../support/browser.ts';

test('raw authoring preserves numeric values through save, reload and backend draft', async ({
  page,
}) => {
  await connect(page);
  const editor = page.getByRole('textbox', {name: /Definition JSON/u});
  await expect(editor).toBeEditable();
  const initial = await editor.inputValue();
  const source = initial
    .replace('"revision":"example-2"', '"revision":"smoke-source"')
    .replace('"parameters":{}', '"parameters":{"temperature":1.0,"seed":9007199254740993}');
  expect(source).not.toBe(initial);
  await editor.fill(source);
  await saveDraft(page);
  await expect(page.getByRole('combobox', {name: 'Experiment', exact: true})).toHaveValue(
    JSON.stringify(['single-agent', 'smoke-source']),
  );
  await expect(editor).toBeEditable();
  await assertNumericSource(editor);
  await page.getByLabel('New revision', {exact: true}).fill('smoke-variant');
  await page.getByRole('button', {name: 'Create draft from saved definition'}).click();
  await expect(editor).toHaveValue(/"revision":"smoke-variant"/u);
  const variant = await editor.inputValue();
  await assertNumericSource(editor);
  expect(variant).toContain('"derived_from":{"graph_id":"single-agent","revision":"smoke-source"}');
});

async function assertNumericSource(editor: Locator): Promise<void> {
  const source = await editor.inputValue();
  expect(source).toContain('9007199254740993');
  expect(source).toContain('"temperature":1.0');
}

async function saveDraft(page: Page): Promise<void> {
  await page.getByRole('button', {name: 'Validate definition', exact: true}).click();
  const save = page.getByRole('button', {name: 'Save definition', exact: true});
  await expect(save).toBeEnabled();
  await save.click();
}
