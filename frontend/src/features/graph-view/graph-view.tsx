import {useState} from 'react';
import type {ReactElement} from 'react';
import {GraphControls} from './graph-controls.tsx';
import {GraphList} from './graph-list.tsx';
import {GraphCanvas} from './graph-canvas.tsx';
import {graphStructure, structureModel} from './structure-model.ts';
import {executionModel} from './execution-model.ts';
import type {GraphViewProps, GraphLayers} from './types.ts';

export function GraphView(props: GraphViewProps): ReactElement {
  const settings = useGraphSettings(props.execution !== undefined);
  return (
    <section aria-label="Grafo del experimento">
      <GraphControls {...settings} />
      <GraphContent {...props} settings={settings} />
    </section>
  );
}
function GraphContent(
  props: GraphViewProps & {readonly settings: ReturnType<typeof useGraphSettings>},
): ReactElement {
  const {settings} = props;
  const structure = graphStructure(props);
  const page = settings.execution ? props.execution : undefined;
  const base = structureModel(structure, settings.layers, settings.expanded);
  const live = executionModel(page, structure, settings.expanded, settings.layers.observed);
  return (
    <>
      {props.detail === undefined && (
        <p>Estructura detallada no disponible. Se muestran los nodos del catálogo.</p>
      )}
      {settings.execution && page === undefined && (
        <p>No hay activaciones registradas disponibles.</p>
      )}
      <GraphCanvas
        key={`${String(settings.layout)}:${props.detail === undefined ? 'fallback' : 'definition'}`}
        nodes={[...base.nodes, ...live.nodes]}
        edges={[...base.edges, ...live.edges]}
        onSelect={props.onSelect}
      />
      <GraphList structure={structure} execution={page} onSelect={props.onSelect} />
    </>
  );
}
interface GraphSettings {
  execution: boolean;
  expanded: boolean;
  layout: number;
  layers: GraphLayers;
  onMode: (value: boolean) => void;
  onExpand: (value: boolean) => void;
  onLayers: (value: GraphLayers) => void;
  onOrganize: () => void;
}
function useGraphSettings(initialExecution: boolean): GraphSettings {
  const [execution, onMode] = useState(initialExecution);
  const [expanded, onExpand] = useState(false);
  const [layers, onLayers] = useState<GraphLayers>({
    control: true,
    permission: false,
    binding: false,
    observed: true,
  });
  const [layout, organize] = useState(0);
  return {
    execution,
    expanded,
    layers,
    onMode,
    onExpand,
    onLayers,
    layout,
    onOrganize: () => {
      organize(layout + 1);
    },
  };
}
