import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, render, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {OperatorClient} from '../src/api/index.ts';
import {ComponentsPage} from '../src/features/catalog/index.ts';
import {FakeApi, failure} from './support/fake-api.ts';
import {catalogBody} from './support/contract.ts';
import {usageBody} from './support/runs.ts';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function serve(catalog: unknown = catalogBody): FakeApi {
  return new FakeApi()
    .on('GET /catalog', {status: 200, body: catalog})
    .on('GET /usage', {status: 200, body: usageBody})
    .install();
}

function renderPage(): void {
  render(<ComponentsPage client={new OperatorClient('credential')} />);
}

function facts(item: HTMLElement): string[][] {
  const terms = within(item).getAllByRole('term');
  return terms.map((term) => [term.textContent, term.nextElementSibling?.textContent ?? '']);
}

function rows(table: HTMLElement): string[][] {
  return within(table)
    .getAllByRole('row')
    .slice(1)
    .map((row) => Array.from(row.children, (cell) => cell.textContent));
}

it('lists every component with its use, ports, state, LLM and configuration', async () => {
  serve();
  renderPage();
  expect(screen.getByRole('heading', {name: 'Components', level: 1})).toBeTruthy();
  expect(screen.getByText(/installs components with/u).textContent).toContain('make components');
  const region = await screen.findByRole('region', {name: 'Components'});
  const names = within(region)
    .getAllByRole('heading', {level: 3})
    .map((name) => name.textContent);
  expect(names).toEqual(['Trigger', 'Output', 'LLM Call', 'Router']);
  const llmCall = within(region).getByRole('listitem', {name: 'LLM Call'});
  expect(within(llmCall).getByText('llm-call@1.0.0')).toBeTruthy();
  expect(within(llmCall).getByText('Installed package')).toBeTruthy();
  expect(facts(llmCall)).toEqual([
    ['Use', 'As a node'],
    ['Inputs', 'in'],
    ['Outputs', 'out'],
    ['State', 'Stateless'],
    ['LLM', 'Chosen for each node in Model'],
    ['Configuration', 'Prompt, Model, Input format, Output format'],
  ]);
  const trigger = within(region).getByRole('listitem', {name: 'Trigger'});
  expect(within(trigger).getByText('Platform')).toBeTruthy();
  expect(within(trigger).getByText('Starts a run by sending its message.')).toBeTruthy();
});

it('shows outputs from the configuration and the embedded use of the Router', async () => {
  serve();
  renderPage();
  const router = await screen.findByRole('listitem', {name: 'Router'});
  expect(facts(router).slice(0, 3)).toEqual([
    ['Use', "As a node, or embedded at a node's outputs"],
    ['Inputs', 'in'],
    ['Outputs', 'Outputs from its configuration'],
  ]);
  const output = screen.getByRole('listitem', {name: 'Output'});
  expect(facts(output).slice(2)).toEqual([
    ['Outputs', 'None'],
    ['State', 'Stateless'],
    ['LLM', 'None'],
    ['Configuration', 'None'],
  ]);
});

it('lists the LLMs with their parameters and the budgets', async () => {
  serve();
  renderPage();
  const llms = await screen.findByRole('region', {name: 'LLMs'});
  const flash = within(llms).getByRole('listitem', {name: 'DeepSeek · DeepSeek Flash'});
  expect(facts(flash)).toEqual([
    ['Provider', 'deepseek'],
    ['Identifier', 'deepseek/deepseek-flash'],
  ]);
  expect(rows(within(flash).getByRole('table', {name: 'Parameters'}))).toEqual([
    ['Reasoning', 'none, low, high, max', 'none'],
    ['Temperature', '0–2', '1'],
    ['Max output tokens', '1–384,000', '1,024'],
  ]);
  const budgets = await screen.findByRole('table', {name: 'Budgets'});
  expect(rows(budgets)).toEqual([
    ['Daily', '2026-10-04', '$1.00', '$0.000083'],
    ['Monthly', '2026-10', '$20.00', '$0.50'],
  ]);
});

it('says when there are no components or LLMs', async () => {
  serve({components: [], llms: []});
  renderPage();
  expect(await screen.findByText('No components are available.')).toBeTruthy();
  expect(screen.getByText('No LLMs are configured.')).toBeTruthy();
});

it('reports a catalog or budget read that fails and tries the catalog again', async () => {
  const api = serve().on('GET /catalog', failure(503, 'unavailable', 'Later.'));
  api.on('GET /usage', failure(503, 'unavailable', 'Later.'));
  renderPage();
  expect((await screen.findByText(/Could not load the catalog/u)).textContent).toContain('Later.');
  expect(await screen.findByText(/Could not load the budgets/u)).toBeTruthy();
  api.on('GET /catalog', {status: 200, body: catalogBody});
  await userEvent.click(screen.getByRole('button', {name: 'Try again'}));
  expect(await screen.findByRole('listitem', {name: 'Router'})).toBeTruthy();
});
