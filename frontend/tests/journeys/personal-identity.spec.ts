import {expect, test} from '@playwright/test';
import {connect, createSession} from '../support/browser.ts';
import {
  deriveRevision,
  editableSource,
  saveRevision,
  selectRevision,
} from '../support/browser-authoring.ts';

test('retains an unusual exact revision through draft, save, reload, selection and Start', async ({
  page,
}) => {
  const revision = 'personal /?% # [1] · Ω';
  await connect(page);
  await deriveRevision(page, revision);
  expect(await editableSource(page)).toContain(`"revision":${JSON.stringify(revision)}`);
  await saveRevision(page, revision);
  await page.reload();
  await connect(page, false);
  await selectRevision(page, revision);
  await createSession(page, 'Exact unusual revision');
  await page.getByLabel('Task or problem').fill('Run the exact selected revision');
  const admitted = page.waitForRequest(
    (request) => request.method() === 'POST' && request.url().endsWith('/runs'),
  );
  await page.getByRole('button', {name: 'Start run', exact: true}).click();
  const body: unknown = JSON.parse((await admitted).postData() ?? '{}');
  expect(body).toMatchObject({graph_id: 'single-agent', graph_revision: revision});
  await expect(page.getByRole('heading', {name: 'Completed', exact: true})).toBeVisible();
  await expect(page.getByRole('region', {name: 'Selected run graph'})).toContainText(
    `single-agent · ${revision}`,
  );
});
