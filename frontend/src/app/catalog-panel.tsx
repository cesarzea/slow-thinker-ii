import {useState} from 'react';
import type {GraphSummary, GraphReference} from '../api/index.ts';
import type {ReactElement} from 'react';
import {
  ComponentInventory,
  ConfigurationSettings,
  useDiscovery,
} from '../features/workspace/index.tsx';
import {GraphWorkspace} from './graph-workspace.tsx';
import {ExecutionWorkspace} from './execution-workspace.tsx';
import {ExperimentPanel} from './experiment-panel.tsx';
import {LibraryControls} from './library-controls.tsx';
import {useCatalog} from './use-catalog.ts';
import {WorkspaceNavigation} from './workspace-navigation.tsx';
import type {WorkspacePage} from './workspace-navigation.tsx';
import {DiscoveryStatus} from './discovery-status.tsx';
interface Props {
  readonly credential: string | undefined;
  readonly generation: number;
}
interface ContentProps extends Props {
  readonly catalog: ReturnType<typeof useCatalog>;
  readonly discovery: ReturnType<typeof useDiscovery>;
  readonly page: WorkspacePage;
}
export function CatalogPanel(props: Props): ReactElement {
  const catalog = useCatalog(props.credential);
  const discovery = useDiscovery(props.credential);
  const [page, select] = useState<WorkspacePage>('Experiments');
  return (
    <div className="product-workspace">
      <WorkspaceNavigation {...{page, select}} />
      <CatalogContent {...props} {...{catalog, discovery, page}} />
    </div>
  );
}
function CatalogContent(props: ContentProps): ReactElement {
  const {graph, model} = props.catalog;
  const onSaved = (reference: GraphReference): void => {
    void model.recoverSaved(reference);
  };
  return (
    <div className="workspace-content">
      <DiscoveryStatus discovery={props.discovery} connected={props.credential !== undefined} />
      <LibrarySelection {...props} />
      <InventoryPages {...props} />
      {graph === null ? (
        <p>Select an available saved experiment to open its workspace.</p>
      ) : (
        <SelectedWorkspace
          {...props}
          graph={graph}
          selectionBlocked={props.catalog.selectionBlocked}
          onSaved={onSaved}
        />
      )}
    </div>
  );
}
function LibrarySelection(props: ContentProps): ReactElement {
  const {graph, graphs, model} = props.catalog;
  return (
    <>
      <div hidden={props.page !== 'Experiments'}>
        <LibraryControls catalog={props.catalog} connected={props.credential !== undefined} />
      </div>
      {graph !== null && (
        <div className="selected-experiment">
          <ExperimentPanel graphs={graphs} graph={graph} onSelect={model.select} />
        </div>
      )}
    </>
  );
}
function InventoryPages(props: ContentProps): ReactElement {
  return (
    <>
      <div hidden={props.page !== 'Components'}>
        <ComponentInventory catalog={props.discovery.catalog} />
      </div>
      <div hidden={props.page !== 'Settings'}>
        {props.credential === undefined ? (
          <p>Connect operator access to edit settings.</p>
        ) : (
          <ConfigurationSettings
            credential={props.credential}
            catalog={props.discovery.catalog}
            refresh={props.discovery.refresh}
          />
        )}
      </div>
    </>
  );
}
interface SelectionProps extends ContentProps {
  readonly graph: GraphSummary;
  readonly onSaved: (reference: GraphReference) => void;
  readonly selectionBlocked: boolean;
}
function SelectedWorkspace(props: SelectionProps): ReactElement {
  return props.credential === undefined ? (
    <div hidden={props.page !== 'Experiments'}>
      <GraphWorkspace
        key={JSON.stringify([props.generation, props.graph.graph_id, props.graph.revision])}
        graph={props.graph}
      />
    </div>
  ) : (
    <ExecutionWorkspace
      credential={props.credential}
      graph={props.graph}
      page={props.page}
      catalog={props.discovery.catalog}
      onSaved={props.onSaved}
      selectionBlocked={props.selectionBlocked}
    />
  );
}
