import type {Page} from '@playwright/test';

const accessToken = 'browser_fixture_operator_token_01234567890123456789';

export async function connect(page: Page, navigate = true): Promise<void> {
  if (navigate) await page.goto('/');
  await page.getByLabel('Clave de acceso').fill(accessToken);
  await page.getByRole('button', {name: 'Conectar para ejecutar'}).click();
}

export async function createSession(page: Page, name: string): Promise<void> {
  await page.getByLabel('Nueva sesión', {exact: true}).fill(name);
  await page.getByRole('button', {name: 'Crear sesión', exact: true}).click();
}
