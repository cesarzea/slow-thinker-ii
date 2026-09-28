import {expect, test} from '@playwright/test';
import type {Page, TestInfo} from '@playwright/test';
import {connect, createSession} from '../support/browser.ts';

test('inspects retained events, call arguments and responses through the actual backend', async ({
  page,
}, info) => {
  await connect(page);
  await createSession(page, 'Browser inspection');
  await page.getByLabel('Problema o tarea').fill('Inspect this run');
  await page.getByRole('button', {name: 'Iniciar ejecución', exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Completada', exact: true})).toBeVisible();
  await page.getByRole('button', {name: 'Inspeccionar ejecución'}).click();
  const events = page.getByRole('region', {name: 'Eventos registrados'});
  const row = events.getByRole('row').filter({hasText: 'call.requested'}).first();
  await row.getByRole('button', {name: /Ver llamada/}).click();
  const call = page.getByRole('region', {name: 'Detalle de llamada'});
  await expect(call).toContainText('USD 0.00000239');
  await call.getByRole('button', {name: 'Ver argumentos'}).click();
  await expect(page.getByRole('region', {name: 'Contenido conservado'})).toContainText('{}');
  await call.getByRole('button', {name: 'Ver respuesta', exact: true}).click();
  await expect(page.getByRole('region', {name: 'Contenido conservado'})).toContainText(
    'Resultado de prueba',
  );
  await page.screenshot({path: info.outputPath('inspection.png'), fullPage: true});
  await inspectActivation(page, info);
  await page.getByRole('button', {name: 'Cerrar inspector'}).click();
  await expect(page.getByRole('region', {name: 'Inspector de ejecución'})).toHaveCount(0);
});

async function inspectActivation(page: Page, info: TestInfo): Promise<void> {
  await page.getByRole('button', {name: 'Ver activación', exact: true}).click();
  const activation = page.getByRole('region', {name: 'Detalle de activación'});
  await expect(activation).toContainText('Agente: worker');
  await activation.getByRole('button', {name: 'Ver salida publicada'}).click();
  await expect(page.getByRole('region', {name: 'Contenido conservado'})).toContainText(
    'Resultado de prueba',
  );
  await page.screenshot({path: info.outputPath('activation.png'), fullPage: true});
}
