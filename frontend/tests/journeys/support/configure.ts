import {expect, type Locator, type Page} from '@playwright/test';
import {apply, openSection} from './session.ts';

export async function setMessage(page: Page, node: string, message: string): Promise<void> {
  const dialog = await openSection(page, node, 'Message');
  await dialog.getByRole('textbox', {name: 'Message sent when the run starts'}).fill(message);
  await apply(dialog);
}

export async function setPrompt(page: Page, node: string, prompt: string): Promise<void> {
  const dialog = await openSection(page, node, 'Prompt');
  await dialog.getByRole('textbox', {name: 'Instructions'}).fill(prompt);
  await apply(dialog);
}

export async function setModel(
  page: Page,
  node: string,
  llm: string,
  tokens: string,
): Promise<void> {
  const dialog = await openSection(page, node, 'Model');
  await dialog.getByRole('combobox', {name: 'LLM'}).selectOption({label: llm});
  await dialog.getByRole('spinbutton', {name: 'Max output tokens'}).fill(tokens);
  await apply(dialog);
}

export async function setScoreOutput(page: Page, node: string): Promise<void> {
  const dialog = await openSection(page, node, 'Output format');
  await dialog.getByRole('combobox', {name: 'Format'}).selectOption({label: 'JSON'});
  await dialog.getByRole('button', {name: 'Add property'}).click();
  const property = dialog.getByRole('group', {name: 'Property 1'});
  await property.getByRole('textbox', {name: 'Property name'}).fill('score');
  await property.getByRole('combobox', {name: 'Type'}).selectOption({label: 'Integer'});
  await property.getByRole('checkbox', {name: 'Required'}).check();
  await property.getByRole('spinbutton', {name: 'Minimum'}).fill('1');
  await property.getByRole('spinbutton', {name: 'Maximum'}).fill('10');
  await apply(dialog);
}

export async function embedRouter(
  page: Page,
  node: string,
  outputs: readonly [string, string],
  script: string,
): Promise<void> {
  await page.getByRole('button', {name: 'Add component'}).click();
  await page
    .getByRole('dialog', {name: 'Add component'})
    .getByRole('button', {name: 'Router'})
    .click();
  const dialog = await openSection(page, node, 'Outputs');
  await fillOutputs(dialog, outputs);
  await dialog.getByRole('tab', {name: 'Script'}).click();
  await dialog.getByRole('textbox', {name: 'route(received, node_input)'}).fill(script);
  await apply(dialog);
}

async function fillOutputs(dialog: Locator, outputs: readonly [string, string]): Promise<void> {
  await dialog.getByRole('textbox', {name: 'Output 1'}).fill(outputs[0]);
  await dialog.getByRole('textbox', {name: 'Output 2'}).fill(outputs[1]);
  await expect(dialog.getByRole('textbox', {name: 'Output 2'})).toHaveValue(outputs[1]);
}
