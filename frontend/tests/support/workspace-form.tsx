import {vi, expect} from 'vitest';
import {fireEvent, render} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {StructuredWorkspace} from '../../src/features/workspace/index.tsx';
import type {ConfigurationCatalog, PatchOperation} from '../../src/api/index.ts';
import {configuration} from './configuration-data.ts';
import collaboration from '../../../docs/contracts/examples/resource-collaboration.graph.json';
const collaborationSource = JSON.stringify(collaboration);
export class WorkspaceForm {
  readonly patch = vi
    .fn<(operations: readonly PatchOperation[]) => Promise<void>>()
    .mockResolvedValue();
  readonly view;
  constructor(
    readonly source = collaborationSource,
    readonly catalog: ConfigurationCatalog | null = configuration,
  ) {
    this.view = render(
      <StructuredWorkspace source={source} catalog={catalog} locked={false} patch={this.patch} />,
    );
  }
  async select(id: string): Promise<void> {
    await userEvent.selectOptions(screen.getByLabelText('Component instance'), id);
  }
  async apply(label: string, value: string): Promise<void> {
    fireEvent.change(screen.getByLabelText(label), {target: {value}});
    await userEvent.click(screen.getByRole('button', {name: `Apply ${label}`}));
  }
  expectPatch(operations: readonly PatchOperation[]): void {
    expect(this.patch).toHaveBeenLastCalledWith(operations);
  }
}
export function setField(label: string, value: string): void {
  fireEvent.change(screen.getByLabelText(label), {target: {value}});
}
export async function choose(label: string, value: string): Promise<void> {
  await userEvent.selectOptions(screen.getByLabelText(label), value);
}
export async function click(label: string): Promise<void> {
  await userEvent.click(screen.getByRole('button', {name: label}));
}
