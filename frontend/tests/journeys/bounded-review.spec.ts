import {expect, test} from '@playwright/test';
import type {Page, Locator} from '@playwright/test';
import {connect, createSession} from '../support/browser.ts';

async function start(page: Page, problem: string): Promise<void> {
  await connect(page);
  await page
    .getByRole('combobox', {name: 'Experimento', exact: true})
    .selectOption('bounded-review');
  await createSession(page, `Bounded ${problem}`);
  await page.getByLabel('Problema o tarea').fill(problem);
  await page.getByRole('button', {name: 'Iniciar ejecución', exact: true}).click();
}
async function openLiveList(page: Page): Promise<ReturnType<Page['getByRole']>> {
  const live = page.getByRole('region', {name: 'Grafo de la ejecución seleccionada'});
  await live.getByText('Explorar componentes, nodos y evidencia en lista').click();
  return live;
}
test('retains feedback and repeated identities through rejection then acceptance', async ({
  page,
}, info) => {
  await start(page, 'accept');
  await expect(page.getByRole('heading', {name: 'Completada', exact: true})).toBeVisible();
  const live = await openLiveList(page);
  await expect(
    live.getByRole('list', {name: 'Activaciones registradas'}).getByRole('listitem'),
  ).toHaveCount(4);
  await expect(live.getByRole('list', {name: 'Activaciones registradas'})).toContainText('revise');
  await expect(live.getByRole('list', {name: 'Activaciones registradas'})).toContainText('accept');
  await page.screenshot({path: info.outputPath('bounded-review-loaded.png'), fullPage: true});
  await inspectAcceptedFeedback(page, live);
  await expect(page.getByRole('region', {name: 'Resultado final'})).toContainText('accepted');
});
test('shows bounded exhaustion with preserved reviews and no accepted result', async ({page}) => {
  await start(page, 'exhaust');
  await expect(page.getByRole('heading', {name: 'Fallida', exact: true})).toBeVisible();
  await expect(page.getByRole('region', {name: 'Estado de ejecución'})).toContainText(
    'activation_limit_reached',
  );
  const live = await openLiveList(page);
  await expect(
    live.getByRole('list', {name: 'Activaciones registradas'}).getByRole('listitem'),
  ).toHaveCount(6);
  await live.getByRole('button', {name: 'Activación #6: review', exact: true}).click();
  const activation = page.getByRole('region', {name: 'Detalle de activación'});
  await expect(activation.getByRole('heading', {level: 3})).toBeInViewport();
  await activation.getByRole('button', {name: 'Ver salida publicada'}).click();
  await expect(page.getByRole('region', {name: 'Contenido conservado'})).toContainText('findings');
  await expect(page.getByRole('region', {name: 'Resultado final'})).toHaveCount(0);
});

async function inspectAcceptedFeedback(page: Page, live: Locator): Promise<void> {
  await page.setViewportSize({width: 390, height: 844});
  await verifyRolesAndContainment(live);
  const chosen = live.getByRole('button', {name: 'Activación #3: propose', exact: true});
  await chosen.focus();
  await chosen.press('Enter');
  const activation = page.getByRole('region', {name: 'Detalle de activación'});
  await expect(activation.getByRole('heading', {level: 3})).toBeFocused();
  await expect(activation.getByRole('heading', {level: 3})).toBeInViewport();
  await activation.getByRole('button', {name: 'Ver entrada efectiva'}).click();
  await expect(page.getByRole('region', {name: 'Contenido conservado'})).toContainText('findings');
  await activation.getByRole('button', {name: 'Ver procedencia de entradas'}).click();
  await expect(page.getByRole('region', {name: 'Contenido conservado'})).toContainText('review');
}
async function verifyRolesAndContainment(live: Locator): Promise<void> {
  await expect(live.getByText('Agente: proposer', {exact: true})).toHaveCount(1);
  await expect(live.getByText('Recurso: proposer-model', {exact: true})).toHaveCount(1);
  await expect(live.getByText('Control: flow', {exact: true})).toHaveCount(1);
  const worker = live.locator('.react-flow__node[data-id="component:review-worker"]');
  await expect(worker).toHaveCount(0);
  await live.getByLabel('Mostrar componentes internos').check();
  await expect(worker).toHaveCount(1);
  await live.getByLabel('Mostrar componentes internos').uncheck();
  await expect(worker).toHaveCount(0);
}
