import {expect, vi} from 'vitest';
import {fireEvent, render} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {z} from 'zod';
import {ConfigurationSettings} from '../../src/features/workspace/index.tsx';
import {configuration} from './configuration-data.ts';
import {reply} from './operator-data.ts';
export function settingsReceipt(body: string, replayed = false): Response {
  const command = z.object({command_id: z.string()}).parse(JSON.parse(body) as unknown);
  return reply({command_id: command.command_id, configuration_revision: 'workspace-2', replayed});
}
export class SettingsView {
  readonly refresh = vi.fn<() => void>();
  readonly bodies: string[] = [];
  readonly fetcher = vi.fn<typeof fetch>().mockImplementation((_, init) => {
    if (typeof init?.body !== 'string') throw new Error('Missing exact command body');
    this.bodies.push(init.body);
    return Promise.resolve(settingsReceipt(init.body));
  });
  readonly view;
  constructor() {
    vi.stubGlobal('fetch', this.fetcher);
    this.view = render(
      <ConfigurationSettings credential="key" catalog={configuration} refresh={this.refresh} />,
    );
  }
  edit(label: string, value: string): void {
    fireEvent.change(screen.getByLabelText(label, {exact: false}), {target: {value}});
  }
  async apply(): Promise<void> {
    await userEvent.click(screen.getByRole('button', {name: 'Apply settings'}));
  }
  expectMessage(text: string): void {
    expect(screen.getByRole('status').textContent).toContain(text);
  }
}
