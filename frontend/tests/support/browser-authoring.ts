import {expect} from '@playwright/test';
import type {Locator, Page} from '@playwright/test';

export function editor(page: Page): Locator {
  return page.getByRole('textbox', {name: /Definition JSON/u});
}

export async function selectRevision(
  page: Page,
  revision: string,
  graphId = 'single-agent',
): Promise<void> {
  await openSource(page);
  const selector = page.getByRole('combobox', {name: 'Experiment', exact: true});
  await selector.selectOption(JSON.stringify([graphId, revision]));
  await openSource(page);
  await expectRevisionSource(page, revision);
  await expect(editor(page)).toBeEditable();
}

export async function saveRevision(
  page: Page,
  revision: string,
  graphId = 'single-agent',
): Promise<void> {
  await openSource(page);
  await page.getByRole('button', {name: 'Validate definition', exact: true}).click();
  const save = page.getByRole('button', {name: 'Save definition', exact: true});
  await expect(save).toBeEnabled();
  await save.click();
  await expect(page.getByRole('combobox', {name: 'Experiment', exact: true})).toHaveValue(
    JSON.stringify([graphId, revision]),
  );
  await openSource(page);
  await expect(editor(page)).toBeEditable();
}

export async function deriveRevision(
  page: Page,
  revision: string,
  graphId = 'single-agent',
): Promise<void> {
  await openSource(page);
  await page.getByLabel('Graph ID', {exact: true}).fill(graphId);
  await page.getByLabel('New revision', {exact: true}).fill(revision);
  await page.getByRole('button', {name: 'Create draft from saved definition'}).click();
  await expectRevisionSource(page, revision);
}

async function expectRevisionSource(page: Page, revision: string): Promise<void> {
  await expect
    .poll(async () =>
      (await editor(page).inputValue()).includes(`"revision":${JSON.stringify(revision)}`),
    )
    .toBe(true);
}

export async function editableSource(page: Page): Promise<string> {
  await openSource(page);
  await expect(editor(page)).toBeEditable();
  return await editor(page).inputValue();
}

export async function openSource(page: Page): Promise<void> {
  await page
    .getByRole('navigation', {name: 'Workspace'})
    .getByRole('button', {name: 'Experiments', exact: true})
    .click();
  await page.getByRole('button', {name: 'JSON source', exact: true}).click();
}
