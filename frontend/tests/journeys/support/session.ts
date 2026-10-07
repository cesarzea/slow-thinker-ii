import {expect, type Locator, type Page} from '@playwright/test';
import {OPERATOR_TOKEN} from './token.ts';

export async function connect(page: Page): Promise<void> {
  await page.goto('/');
  await page.getByRole('textbox', {name: 'Operator token'}).fill(OPERATOR_TOKEN);
  await page.getByRole('button', {name: 'Connect'}).click();
  await expect(page.getByRole('heading', {name: 'Graphs'})).toBeVisible();
}

export async function newGraph(page: Page, name: string): Promise<void> {
  await page.getByRole('button', {name: 'New graph'}).click();
  const dialog = page.getByRole('dialog', {name: 'New graph'});
  await dialog.getByRole('textbox', {name: 'Name'}).fill(name);
  await dialog.getByRole('button', {name: 'Create'}).click();
  await expect(page.getByRole('button', {name: 'Add Trigger'})).toBeVisible();
}

export function selectedPanel(page: Page): Locator {
  return page.getByRole('complementary', {name: 'Selected node'});
}

export async function addNode(page: Page, label: string, name: string): Promise<void> {
  await page.getByRole('button', {name: `Add ${label}`}).click();
  const field = selectedPanel(page).getByRole('textbox', {name: 'Node name'});
  await field.fill(name);
  await field.press('Enter');
  await expect(page.getByRole('group', {name, exact: true})).toBeVisible();
}

export async function selectNode(page: Page, name: string): Promise<void> {
  await page.getByRole('group', {name, exact: true}).click();
  await expect(selectedPanel(page).getByRole('heading', {name})).toBeVisible();
}

export async function openSection(page: Page, node: string, section: string): Promise<Locator> {
  await selectNode(page, node);
  await selectedPanel(page)
    .getByRole('button', {name: `Edit ${section}`})
    .click();
  const dialog = page.getByRole('dialog', {name: node});
  await expect(dialog).toBeVisible();
  return dialog;
}

export async function apply(dialog: Locator): Promise<void> {
  await dialog.getByRole('button', {name: 'Apply'}).click();
  await expect(dialog).toBeHidden();
}

export async function connectPorts(
  page: Page,
  from: readonly [string, string],
  to: readonly [string, string],
): Promise<void> {
  await selectNode(page, from[0]);
  const choice = selectedPanel(page).getByRole('combobox', {name: `Connect ${from[1]} to`});
  await choice.selectOption({label: `${to[0]} · ${to[1]}`});
  await expect(
    selectedPanel(page).getByRole('button', {name: `Remove connection to ${to[0]} · ${to[1]}`}),
  ).toBeVisible();
}

/** Every edit saves itself; this waits until the last one is stored. */
export async function saved(page: Page): Promise<void> {
  await expect(
    page
      .getByRole('status')
      .filter({hasText: /^Saved/u})
      .first(),
  ).toBeVisible();
}
