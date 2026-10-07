import {expect, test} from '@playwright/test';
import {embedRouter, setMessage, setModel, setPrompt, setScoreOutput} from './support/configure.ts';
import {expectResult, expectStatus, runGraph} from './support/runs.ts';
import {addNode, connect, connectPorts, newGraph, saved} from './support/session.ts';

const STORY = 'A dog opened a bakery for pigeons.';
const SCRIPT = [
  'def route(received, node_input):',
  '    if received["score"] >= 7:',
  '        return "funny", node_input',
  '    return "not_funny", node_input',
].join('\n');

test('J2: an embedded Router gives the agent two outputs', async ({page}) => {
  await connect(page);
  await newGraph(page, 'Story triage');
  await addNode(page, 'Trigger', 'Story');
  await addNode(page, 'LLM Call', 'Judge');
  await setPrompt(page, 'Judge', 'Rate how funny this story is from 1 to 10.');
  await setModel(page, 'Judge', 'OpenAI · GPT-6 Luna', '50');
  await setScoreOutput(page, 'Judge');
  await embedRouter(page, 'Judge', ['funny', 'not_funny'], SCRIPT);
  await expect(page.getByRole('button', {name: 'Judge output funny'})).toBeVisible();
  await expect(page.getByRole('button', {name: 'Judge output out'})).toHaveCount(0);
  await addNode(page, 'Output', 'Funny');
  await addNode(page, 'Output', 'Not funny');
  await connectPorts(page, ['Story', 'out'], ['Judge', 'in']);
  await connectPorts(page, ['Judge', 'funny'], ['Funny', 'in']);
  await connectPorts(page, ['Judge', 'not_funny'], ['Not funny', 'in']);
  await setMessage(page, 'Story', STORY);
  await saved(page);
  await runGraph(page, STORY);
  await expectStatus(page, 'Completed');
  await expectResult(page, 'Funny', STORY);
});
