import {expect, test} from '@playwright/test';
import {setMessage, setModel, setPrompt} from './support/configure.ts';
import {expectResult, expectStatus, runGraph, runPanel} from './support/runs.ts';
import {
  addNode,
  connect,
  connectPorts,
  newGraph,
  saved,
  selectedPanel,
  selectNode,
} from './support/session.ts';

const STORY = 'A cat tried to learn to fly.';

test('J1: one agent makes a story funny', async ({page}) => {
  await connect(page);
  await newGraph(page, 'Funny story');
  await addNode(page, 'Trigger', 'Story');
  await addNode(page, 'LLM Call', 'Proposer');
  await addNode(page, 'Output', 'Funny story');
  await connectPorts(page, ['Story', 'out'], ['Proposer', 'in']);
  await connectPorts(page, ['Proposer', 'out'], ['Funny story', 'in']);
  await selectNode(page, 'Proposer');
  await expect(selectedPanel(page)).toContainText('Not set');
  await page.getByRole('button', {name: 'Run', exact: true}).click();
  await expect(runPanel(page).getByRole('button', {name: 'Execute'})).toBeDisabled();
  await page.getByRole('button', {name: 'Edit', exact: true}).click();
  await setPrompt(page, 'Proposer', 'Rewrite this story so that it is funny.');
  await setModel(page, 'Proposer', 'OpenAI · GPT-6 Luna', '300');
  await setMessage(page, 'Story', STORY);
  await expect(page.getByText(/permission|slot/i)).toHaveCount(0);
  await saved(page);
  await runGraph(page, STORY);
  await expectStatus(page, 'Completed');
  await expectResult(page, 'Funny story', `Simulated reply to: ${STORY}`);
});
