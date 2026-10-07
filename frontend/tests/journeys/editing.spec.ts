import {expect, test} from '@playwright/test';
import {addNode, connect, newGraph, saved} from './support/session.ts';

test('AC01: an output port connects to an input port by dragging', async ({page}) => {
  await connect(page);
  await newGraph(page, 'Dragged connection');
  await addNode(page, 'Trigger', 'Story');
  await addNode(page, 'Output', 'Result');
  const output = page.getByRole('button', {name: 'Story output out'});
  await output.dragTo(page.getByRole('button', {name: 'Result input in'}));
  await expect(
    page.getByRole('img', {name: 'Connection from Story · out to Result · in'}),
  ).toBeVisible();
});

test('AC09: every edit is saved as it is made and survives a reload', async ({page}) => {
  await connect(page);
  await newGraph(page, 'Draft survives');
  await addNode(page, 'Trigger', 'Story');
  await addNode(page, 'Output', 'Result');
  await saved(page);
  await page.reload();
  await expect(page.getByRole('group', {name: 'Result', exact: true})).toBeVisible();
});
