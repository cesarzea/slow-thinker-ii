import type {Page} from '@playwright/test';
import {embedRouter, setMessage, setModel, setPrompt, setScoreOutput} from './configure.ts';
import {addNode, connectPorts, newGraph} from './session.ts';

export const STORY = 'A cat tried to learn to fly.';
const SCRIPT = [
  'def route(received, node_input):',
  '    if received["score"] >= 7:',
  '        return "accepted", node_input',
  '    return "revise", node_input',
].join('\n');

export async function buildReviewLoop(page: Page, name: string): Promise<void> {
  await newGraph(page, name);
  await addNode(page, 'Trigger', 'Story');
  await addNode(page, 'LLM Call', 'Proposer');
  await addNode(page, 'LLM Call', 'Reviewer');
  await addNode(page, 'Output', 'Funny story');
  await setPrompt(page, 'Proposer', 'Rewrite this story so that it is funny.');
  await setModel(page, 'Proposer', 'OpenAI · GPT-6 Luna', '300');
  await setPrompt(page, 'Reviewer', 'Rate how funny this story is from 1 to 10.');
  await setModel(page, 'Reviewer', 'DeepSeek · DeepSeek Flash', '50');
  await setScoreOutput(page, 'Reviewer');
  await embedRouter(page, 'Reviewer', ['accepted', 'revise'], SCRIPT);
  await connectPorts(page, ['Story', 'out'], ['Proposer', 'in']);
  await connectPorts(page, ['Proposer', 'out'], ['Reviewer', 'in']);
  await connectPorts(page, ['Reviewer', 'revise'], ['Proposer', 'in']);
  await connectPorts(page, ['Reviewer', 'accepted'], ['Funny story', 'in']);
  await setMessage(page, 'Story', STORY);
}

/** The run limits, in the graph's own panel with no node selected. */
export async function setLimits(page: Page, activations: string, budget: string): Promise<void> {
  await page.locator('.react-flow__pane').click({position: {x: 10, y: 10}});
  const graph = page.getByRole('complementary', {name: 'Graph'});
  const maximum = graph.getByRole('spinbutton', {name: 'Maximum activations'});
  await maximum.fill(activations);
  await maximum.press('Enter');
  const money = graph.getByRole('textbox', {name: 'Budget per run ($)'});
  await money.fill(budget);
  await money.press('Enter');
}
