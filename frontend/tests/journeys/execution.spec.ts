import {expect, test} from '@playwright/test';
import {connect, createSession} from '../support/browser.ts';

const input = 'Problema o tarea';
const start = 'Iniciar ejecución';

test('creates a saved session, executes, inspects results and recovers history after reload', async ({
  page,
}, info) => {
  await connect(page);
  await createSession(page, 'Browser completion');
  await page.getByLabel(input).fill('A private task');
  await page.getByRole('button', {name: start, exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Completada', exact: true})).toBeVisible();
  await expect(page.getByRole('region', {name: 'Resultado final'})).toContainText(
    'Resultado de prueba',
  );
  await expect(page.getByRole('region', {name: 'Estado de ejecución'})).toContainText(
    'USD 0.00000239',
  );
  expect(await page.evaluate(() => JSON.stringify(localStorage))).not.toContain('A private task');
  await page.screenshot({path: info.outputPath('execution-result.png'), fullPage: true});
  await page.reload();
  await connect(page, false);
  const history = page.getByRole('region', {name: 'Historial de la sesión'});
  await history.getByRole('button').first().click();
  await expect(page.getByRole('heading', {name: 'Completada', exact: true})).toBeVisible();
});

test('Stop closes a running execution while preserving uncertain spending', async ({page}) => {
  await connect(page);
  await createSession(page, 'Browser stop');
  await page.getByLabel(input).fill('wait');
  await page.getByRole('button', {name: start, exact: true}).click();
  await expect(page.getByRole('heading', {name: 'En curso', exact: true})).toBeVisible();
  await page.getByRole('button', {name: 'Detener ejecución', exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Cancelada', exact: true})).toBeVisible();
  await expect(page.getByRole('region', {name: 'Estado de ejecución'})).toContainText(
    'USD 0.000003 pendiente',
  );
  await expect(page.getByRole('region', {name: 'Resultado final'})).toHaveCount(0);
});
