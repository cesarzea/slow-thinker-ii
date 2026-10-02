import {expectWorkspaceFits} from '../support/browser-workspace.ts';
import {expect, test} from '@playwright/test';
import {connect} from '../support/browser.ts';
import {editableSource, editor} from '../support/browser-authoring.ts';
test('keeps forms and keyboard navigation usable on a narrow workspace', async ({page}) => {
  await page.setViewportSize({width: 390, height: 844});
  await connect(page);
  const source = `${await editableSource(page)}\n`;
  await editor(page).fill(source);
  const nav = page.getByRole('navigation', {name: 'Workspace'});
  for (const name of ['Components', 'Resources', 'Runs', 'Settings', 'Experiments']) {
    const button = nav.getByRole('button', {name, exact: true});
    await button.focus();
    await page.keyboard.press('Enter');
    await expect(button).toHaveAttribute('aria-current', 'page');
    await expectWorkspaceFits(page);
  }
  expect(await editableSource(page)).toBe(source);
  await expect(page.getByRole('button', {name: 'Discard draft', exact: true})).toBeVisible();
});
