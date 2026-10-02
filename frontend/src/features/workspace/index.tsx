import type {ReactElement} from 'react';
import {sourceTree} from '../../ui/index.ts';
import {InstanceEditor} from './instance-editor.tsx';
import {GraphEditor} from './graph-editor.tsx';
import type {SourceWorkspaceProps} from './types.ts';
export type {SourceWorkspaceProps} from './types.ts';
export {useDiscovery} from './use-discovery.ts';
export {ComponentInventory} from './inventory.tsx';
export {ResourceInventory} from './resource-inventory.tsx';
export {ConfigurationSettings} from './settings.tsx';

export function StructuredWorkspace(props: SourceWorkspaceProps): ReactElement {
  if (sourceTree(props.source) === null)
    return (
      <p role="status">
        Structured forms require readable JSON within the preview nesting bound. Use the JSON editor
        to correct the source.
      </p>
    );
  return (
    <div className="structured-workspace">
      <p>
        Apply each form value to the unsaved source, then validate and save a revision. Unapplied
        field values do not change the saved experiment.
      </p>
      <InstanceEditor {...props} />
      <GraphEditor {...props} />
    </div>
  );
}
