import {expect, test} from '@playwright/test';
import type {Page} from '@playwright/test';
import {connect, createSession} from '../support/browser.ts';
import {
  deriveRevision,
  editableSource,
  openSource,
  saveRevision,
} from '../support/browser-authoring.ts';
import {
  applyField,
  collaborationCanvas,
  importCollaboration,
  runCollaboration,
  workspacePage,
} from '../support/browser-workspace.ts';
test('configures registered resources through lossless forms and executes an exact personal revision', async ({
  page,
}) => {
  await connect(page);
  await workspacePage(page, 'Components');
  await expect(page.getByRole('cell', {name: 'contextual-call 0.1.0'})).toBeVisible();
  await expect(page.getByRole('cell', {name: 'example.resource-agent 0.1.0'})).toBeVisible();
  await importCollaboration(page);
  await configurePrompt(page);
  await resourcesAndNavigation(page);
  await saveRevision(page, 'example-1', 'browser-collaboration');
  await createSession(page, 'Configured collaboration');
  await runCollaboration(page);
  await collaborationCanvas(page);
  await deriveRevision(page, 'next-2', 'browser-collaboration');
  await page.getByRole('button', {name: 'Structured forms', exact: true}).click();
  await page
    .getByRole('combobox', {name: 'Component instance', exact: true})
    .selectOption('reviewer-worker');
  await applyField(page, 'instructions', 'The next revision prompt.');
  await saveRevision(page, 'next-2', 'browser-collaboration');
  await collaborationCanvas(page);
  await page.getByRole('button', {name: 'Inspect run', exact: true}).click();
  await expect(page.getByRole('complementary', {name: 'Technical evidence'})).toBeVisible();
  await expect(page.getByRole('region', {name: 'Recorded events'})).toContainText('call.requested');
});
async function configurePrompt(page: Page): Promise<void> {
  await page.getByRole('button', {name: 'Structured forms', exact: true}).click();
  await page
    .getByRole('combobox', {name: 'Component instance', exact: true})
    .selectOption('proposer-worker');
  await expect(page.getByRole('textbox', {name: 'instructions', exact: true})).toHaveValue(
    /Propose a concise/u,
  );
  await applyField(page, 'instructions', 'A source-preserving configured prompt.');
  await openSource(page);
  const source = await editableSource(page);
  expect(source).toContain('A source-preserving configured prompt.');
  expect(source).toContain('9007199254740993');
  expect(source).toContain('"temperature":1.0');
  await createSession(page, 'Dirty configuration');
  await page.getByLabel('Task or problem').fill('Unsaved input');
  await expect(page.getByRole('button', {name: 'Start run', exact: true})).toBeDisabled();
  await expect(page.getByText(/has unsaved changes/u)).toBeVisible();
}
async function resourcesAndNavigation(page: Page): Promise<void> {
  await workspacePage(page, 'Resources');
  const inventory = page.getByRole('region', {name: 'Experiment resource inventory'});
  await expect(inventory.getByText('Namespace: collaboration')).toBeVisible();
  await expect(inventory.getByText('Retention: persistent')).toBeVisible();
  await expect(
    inventory.getByText('Shared by selected consumers · proposer, reviewer'),
  ).toHaveCount(2);
  await workspacePage(page, 'Settings');
  await expect(page.getByText(/Changing a cap never resets/u)).toBeVisible();
  await openSource(page);
  expect(await editableSource(page)).toContain('A source-preserving configured prompt.');
}
