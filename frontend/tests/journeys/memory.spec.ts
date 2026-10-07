import {expect, test, type Page} from '@playwright/test';
import {embedRouter, setMessage, setModel, setPrompt} from './support/configure.ts';
import {expectStatus, runGraph, runPanel} from './support/runs.ts';
import {
  addNode,
  connect,
  connectPorts,
  newGraph,
  saved,
  selectNode,
  selectedPanel,
} from './support/session.ts';

const STORY = 'A cat tried to learn to fly.';
/** Back to the Editor until its reply carries what it remembered. */
const SCRIPT = [
  'def route(received, node_input):',
  '    if "Conversation so far:" in received:',
  '        return "done", received',
  '    return "again", received',
].join('\n');

/** An Editor with a Memory whose Router sends its first reply back to it. */
async function buildEditingLoop(page: Page): Promise<void> {
  await newGraph(page, 'Editor with memory');
  await addNode(page, 'Trigger', 'Story');
  await addNode(page, 'LLM Call', 'Editor');
  await setPrompt(page, 'Editor', 'Rewrite this story so that it is funny.');
  await setModel(page, 'Editor', 'OpenAI · GPT-6 Luna', '300');
  await embedRouter(page, 'Editor', ['again', 'done'], SCRIPT);
  await addNode(page, 'Output', 'Edited story');
  await connectPorts(page, ['Story', 'out'], ['Editor', 'in']);
  await connectPorts(page, ['Editor', 'again'], ['Editor', 'in']);
  await connectPorts(page, ['Editor', 'done'], ['Edited story', 'in']);
  await setMessage(page, 'Story', STORY);
}

test('Memory: a node remembers its earlier exchange when its next message arrives', async ({
  page,
}) => {
  await connect(page);
  await buildEditingLoop(page);
  await selectNode(page, 'Editor');
  await page.getByRole('button', {name: 'Add Memory'}).click();
  await expect(selectedPanel(page)).toContainText('with Router and Memory');
  await saved(page);
  await runGraph(page, STORY);
  await expectStatus(page, 'Completed');
  const points = page.getByRole('navigation', {name: 'Observation points'});
  await points.getByRole('button', {name: 'Show what Editor records'}).click();
  const facets = points.getByRole('list', {name: 'What Editor records'});
  await facets.getByRole('button', {name: 'Memory'}).click();
  const feed = runPanel(page).getByRole('region', {name: 'Activity of Editor · Memory'});
  await expect(feed.getByRole('listitem').first()).toContainText(STORY);
  const recalled = feed.getByRole('listitem').filter({hasText: 'Conversation so far:'});
  await expect(recalled.first()).toBeVisible();
});
