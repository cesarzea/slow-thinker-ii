import {Buffer} from 'node:buffer';
import {expect, test} from '@playwright/test';
import type {Page} from '@playwright/test';
import {connect, createSession} from '../support/browser.ts';
import {expectSavedRunCanvas, openProposerCall} from '../support/saved-run-canvas.ts';
import {
  deriveRevision,
  editableSource,
  editor,
  saveRevision,
  selectRevision,
} from '../support/browser-authoring.ts';

test('imports, edits, saves and executes exact revisions while keeping historical evidence', async ({
  page,
}, info) => {
  await connect(page);
  await importPersonal(page);
  await reloadAndRun(page);
  await deriveRevision(page, 'authoring-v2');
  await editor(page).fill(
    (await editableSource(page)).replace(
      'Imported personal instructions.',
      'Second revision instructions.',
    ),
  );
  await saveRevision(page, 'authoring-v2');
  await verifyIndependentRevisions(page);
  await inspectHistoricalRun(page);
  await deriveRevision(page, 'variant-v1', 'authoring-manual-variant');
  expect(await editableSource(page)).toContain(
    '"derived_from":{"graph_id":"single-agent","revision":"authoring-v2"}',
  );
  await saveRevision(page, 'variant-v1', 'authoring-manual-variant');
  await expectSavedRunCanvas(page, 'single-agent', 'authoring-v1');
  await runManualVariant(page);
  await page.screenshot({
    path: info.outputPath('personal-authoring-and-history.png'),
    fullPage: true,
  });
});

async function importPersonal(page: Page): Promise<void> {
  const initial = await editableSource(page);
  const source = initial
    .replace('"revision":"example-2"', '"revision":"authoring-v1"')
    .replace('Propose a solution to the supplied problem.', 'Imported personal instructions.');
  await page.getByLabel('Import UTF-8 JSON file').setInputFiles({
    name: 'personal.json',
    mimeType: 'application/json',
    buffer: Buffer.from(source),
  });
  await expect(editor(page)).toHaveValue(source);
  await editor(page).fill(`${source}\n`);
  await createSession(page, 'Personal authoring');
  await page.getByLabel('Task or problem').fill('Draft input');
  await expect(page.getByRole('button', {name: 'Start run', exact: true})).toBeDisabled();
  await page.getByRole('button', {name: 'Validate definition', exact: true}).click();
  await expect(
    page.getByText(/Definition validation passed for single-agent · authoring-v1/u),
  ).toBeVisible();
  await expect(page.getByRole('button', {name: 'Start run', exact: true})).toBeDisabled();
  await saveRevision(page, 'authoring-v1');
}

async function reloadAndRun(page: Page): Promise<void> {
  await page.reload();
  await connect(page, false);
  await selectRevision(page, 'authoring-v1');
  expect(await editableSource(page)).toContain('Imported personal instructions.');
  await page.getByLabel('Task or problem').fill('Execute the saved personal revision');
  await page.getByRole('button', {name: 'Start run', exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Completed', exact: true})).toBeVisible();
  await expect(page.getByRole('region', {name: 'Final result'})).toContainText('Test result');
  await expectSavedRunCanvas(page, 'single-agent', 'authoring-v1');
  expect(await page.evaluate(() => JSON.stringify(localStorage))).not.toContain(
    'Imported personal instructions.',
  );
}

async function verifyIndependentRevisions(page: Page): Promise<void> {
  await selectRevision(page, 'authoring-v1');
  expect(await editableSource(page)).toContain('Imported personal instructions.');
  expect(await editableSource(page)).not.toContain('Second revision instructions.');
  await selectRevision(page, 'authoring-v2');
  expect(await editableSource(page)).toContain('Second revision instructions.');
  await expectSavedRunCanvas(page, 'single-agent', 'authoring-v1');
}

async function runManualVariant(page: Page): Promise<void> {
  const graphId = 'authoring-manual-variant';
  await page.getByLabel('Task or problem').fill('Execute the saved manual variant');
  await page.getByRole('button', {name: 'Start run', exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Completed', exact: true})).toBeVisible();
  await expectSavedRunCanvas(page, graphId, 'variant-v1');
  await deriveRevision(page, 'variant-v2', graphId);
  await editor(page).fill(
    (await editableSource(page)).replace(
      'Second revision instructions.',
      'Next manual variant instructions.',
    ),
  );
  await saveRevision(page, 'variant-v2', graphId);
  await expectSavedRunCanvas(page, graphId, 'variant-v1');
  await inspectHistoricalRun(page);
}

async function inspectHistoricalRun(page: Page): Promise<void> {
  await page.getByRole('button', {name: 'Inspect run', exact: true}).click();
  await openProposerCall(page);
  await page
    .getByRole('region', {name: 'Call details'})
    .getByRole('button', {name: 'View response', exact: true})
    .click();
  await expect(page.getByRole('region', {name: 'Retained content'})).toContainText('Test result');
  await page.getByRole('button', {name: 'Close inspector', exact: true}).click();
}
