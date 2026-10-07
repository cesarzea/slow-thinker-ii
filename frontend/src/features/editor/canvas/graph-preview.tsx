import {useMemo, useState} from 'react';
import type {ReactElement} from 'react';
import {ReactFlowProvider} from '@xyflow/react';
import type {Catalog, GraphDocument} from '../../../api/index.ts';
import {moveNode} from '../state/document.ts';
import {useCanvasInteraction} from './canvas-interaction.tsx';
import type {CanvasInteraction} from './canvas-interaction.tsx';
import type {CanvasModel} from './canvas-model.ts';
import {CanvasToolbar} from './canvas-toolbar.tsx';
import {viewOf} from './connection-style.ts';
import {flowEdges, flowNodes} from './flow-model.ts';
import {GraphCanvas} from './graph-canvas.tsx';
import {ObservationContext} from './observation-dot.tsx';
import type {CanvasObservation} from './observation-dot.tsx';
import {Outline} from './outline.tsx';
import {useViewModel} from './use-view-model.ts';

export interface GraphPreviewProps {
  readonly document: GraphDocument;
  readonly catalog: Catalog;
  /** Activation and message counts; without them the canvas shows no badges or labels. */
  readonly activations?: Readonly<Record<string, number>>;
  readonly messages?: Readonly<Record<string, number>>;
  /** The editor's toolbar and draggable cards, changing this view only; nothing is saved. */
  readonly arrangeable?: boolean;
  /** Run mode's observation points, a dot at the middle of each connection. */
  readonly observation?: CanvasObservation;
}

function useFlow(props: GraphPreviewProps, document: GraphDocument, curvature: number | null) {
  const {catalog, activations, messages} = props;
  return useMemo(() => {
    const input = {
      document,
      catalog,
      editable: false,
      ...(activations === undefined ? {} : {activations}),
      ...(messages === undefined ? {} : {messages}),
    };
    const nodes = flowNodes(input);
    const saved = viewOf(document);
    const view = curvature === null ? saved : {...saved, curvature};
    return {nodes, edges: flowEdges(input, nodes), view};
  }, [document, catalog, activations, messages, curvature]);
}

function PreviewCanvas(
  props: GraphPreviewProps & {
    readonly model: CanvasModel | null;
    readonly curvature: number | null;
    readonly interaction?: CanvasInteraction;
  },
): ReactElement {
  const {model, interaction} = props;
  const flow = useFlow(props, model?.document ?? props.document, props.curvature);
  return (
    <GraphCanvas
      nodes={flow.nodes}
      edges={flow.edges}
      view={flow.view}
      editable={false}
      label="Run graph"
      {...(model === null || interaction === undefined
        ? {}
        : {
            movable: true,
            interaction,
            onMove: (nodeId: string, position: [number, number]) => {
              model.change((value) => moveNode(value, nodeId, position));
            },
          })}
    />
  );
}

/** A run's graph with the editor's toolbar; its changes stay in this view. */
function ArrangeablePreview(props: GraphPreviewProps): ReactElement {
  const model = useViewModel(props.document);
  const [outline, setOutline] = useState(false);
  const [curvature, setCurvature] = useState<number | null>(null);
  const interaction = useCanvasInteraction();
  return (
    <div className="graph-preview">
      <CanvasToolbar
        model={model}
        catalog={props.catalog}
        outline={outline}
        onOutline={setOutline}
        manual={interaction.manual}
        onPreview={setCurvature}
      />
      {outline ? (
        <Outline document={model.document} catalog={props.catalog} />
      ) : (
        <PreviewCanvas {...props} model={model} curvature={curvature} interaction={interaction} />
      )}
    </div>
  );
}

/** A read-only canvas of a saved graph, with activation and message counts when given. */
export function GraphPreview(props: GraphPreviewProps): ReactElement {
  return (
    <ReactFlowProvider>
      <ObservationContext value={props.observation ?? null}>
        {props.arrangeable === true ? (
          <ArrangeablePreview {...props} />
        ) : (
          <PreviewCanvas {...props} model={null} curvature={null} />
        )}
      </ObservationContext>
    </ReactFlowProvider>
  );
}
