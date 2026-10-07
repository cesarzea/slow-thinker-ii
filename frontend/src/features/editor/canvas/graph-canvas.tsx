import {useRef} from 'react';
import type {ReactElement} from 'react';
import {Background, ReactFlow} from '@xyflow/react';
import {behaviour} from './canvas-behaviour.ts';
import {CanvasControls, CanvasFraming, useCanvasInteraction} from './canvas-interaction.tsx';
import type {CanvasInteraction} from './canvas-interaction.tsx';
import {markActive, useHovered} from './edge-activity.ts';
import {useEdgeSelection} from './edge-selection.ts';
import {CanvasContexts} from './canvas-contexts.tsx';
import {NodeCard} from './node-card.tsx';
import {useCardMenu} from './card-menu.tsx';
import type {ConnectionView} from './connection-style.ts';
import type {NodeActions} from './node-actions.ts';
import {usePortTips} from './port-tip.tsx';
import {RouteEdge} from './route-edge.tsx';
import {useComponentDrop} from './use-component-drop.ts';
import {useFlowNodes} from './use-flow-nodes.ts';
import type {FlowCallbacks} from './use-flow-nodes.ts';
import type {CardNode, RouteEdgeType} from './types.ts';
import './canvas.css';

export interface GraphCanvasProps {
  readonly nodes: CardNode[];
  readonly edges: RouteEdgeType[];
  readonly editable: boolean;
  /** Cards can be dragged, reported through `onMove`, on a canvas that is not editable. */
  readonly movable?: boolean;
  readonly label: string;
  readonly onSelect?: (nodeId: string | null) => void;
  readonly onMove?: (nodeId: string, position: [number, number]) => void;
  readonly onConnect?: (from: string, to: string) => void;
  readonly onDisconnect?: (from: string, to: string) => void;
  /** Adds the component dropped from the palette at this canvas position. */
  readonly onDropComponent?: (
    component: string,
    position: [number, number],
    nodeId: string | null,
  ) => void;
  /** Shared with a toolbar outside the canvas; the canvas then shows no controls of its own. */
  readonly interaction?: CanvasInteraction;
  /** Editing, deleting and removing a component from a card; editable canvases only. */
  readonly nodeActions?: NodeActions;
  /** How connections are drawn: the graph's own view. */
  readonly view: ConnectionView;
}

const nodeTypes = {card: NodeCard};
const edgeTypes = {route: RouteEdge};

function flowCallbacks(props: GraphCanvasProps): FlowCallbacks {
  if (props.editable) return props;
  return props.movable === true ? {onMove: props.onMove} : {};
}

/** The canvas's state: view interaction, palette drops, cards, and the chosen connection. */
function useCanvasModel(props: GraphCanvasProps) {
  const own = useCanvasInteraction();
  return {
    interaction: props.interaction ?? own,
    drop: useComponentDrop(props.editable ? props.onDropComponent : undefined),
    flow: useFlowNodes(props.nodes, flowCallbacks(props)),
    selection: useEdgeSelection(props.edges, props.editable ? props.onDisconnect : undefined),
    hover: useHovered(),
  };
}

type Model = ReturnType<typeof useCanvasModel>;

/** React Flow with the cards and connections, editing and the card menu when editable. */
function Flow(props: {
  readonly canvas: GraphCanvasProps;
  readonly model: Model;
  readonly onNodeContextMenu: ReturnType<typeof useCardMenu>['onNodeContextMenu'];
  /** Opens a card's configuration on double click; editable canvases only. */
  readonly onNodeOpen?: (nodeId: string) => void;
}): ReactElement {
  const {canvas, model} = props;
  const {interaction, drop, flow, selection, hover} = model;
  return (
    <ReactFlow<CardNode, RouteEdgeType>
      nodes={flow.nodes}
      edges={markActive(canvas.edges, selection.selected, hover.hovered)}
      nodeTypes={nodeTypes}
      edgeTypes={edgeTypes}
      onNodesChange={flow.onNodesChange}
      {...behaviour(canvas, selection, interaction, drop)}
      {...hover.events}
      onNodeContextMenu={props.onNodeContextMenu}
      onNodeDoubleClick={(_event, node) => {
        props.onNodeOpen?.(node.id);
      }}
    >
      <Background gap={18} size={1.2} color="var(--line-strong)" />
      {canvas.interaction === undefined && <CanvasControls manualRef={interaction.manual} />}
      <CanvasFraming count={flow.nodes.length} manualRef={interaction.manual} />
    </ReactFlow>
  );
}

/**
 * The graph canvas: React Flow with one handle per effective port, and every connection
 * curved or routed around the cards. On an editable canvas a connection is selected with a
 * click and removed with its × button, Delete or Backspace; a card has its own menu.
 */
export function GraphCanvas(props: GraphCanvasProps): ReactElement {
  const model = useCanvasModel(props);
  const frame = useRef<HTMLElement>(null);
  const tips = usePortTips(frame);
  const actions = props.editable ? (props.nodeActions ?? null) : null;
  const cardMenu = useCardMenu(frame, actions);
  const remove = props.editable ? model.selection.remove : null;
  const className = props.editable ? 'graph-canvas editable' : 'graph-canvas';
  return (
    <section ref={frame} className={className} aria-label={props.label}>
      <CanvasContexts
        edges={props.edges}
        view={props.view}
        tips={tips.tips}
        remove={remove}
        actions={actions}
      >
        <Flow
          canvas={props}
          model={model}
          onNodeContextMenu={cardMenu.onNodeContextMenu}
          {...(actions === null ? {} : {onNodeOpen: actions.edit})}
        />
      </CanvasContexts>
      {tips.tip}
      {cardMenu.menu}
    </section>
  );
}
