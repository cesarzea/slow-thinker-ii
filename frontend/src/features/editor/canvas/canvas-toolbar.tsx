import type {ReactElement} from 'react';
import {useReactFlow, useStore} from '@xyflow/react';
import type {Catalog} from '../../../api/index.ts';
import {Button, IconButton} from '../../../ui/index.ts';
import type {CanvasModel} from './canvas-model.ts';
import {FIT_VIEW} from './canvas-interaction.tsx';
import type {ManualViewport} from './canvas-interaction.tsx';
import type {CardNode, RouteEdgeType} from './types.ts';
import {Arrange} from './arrange-button.tsx';
import {ConnectionsMenu} from './connections-menu.tsx';

interface Props {
  readonly model: CanvasModel;
  readonly catalog: Catalog;
  readonly outline: boolean;
  readonly onOutline: (outline: boolean) => void;
  readonly manual: ManualViewport;
  readonly onPreview: (curvature: number | null) => void;
}

const MAC = typeof navigator !== 'undefined' && /Mac|iP(hone|ad)/u.test(navigator.platform);
const SHORTCUTS = MAC ? {undo: '⌘Z', redo: '⇧⌘Z'} : {undo: 'Ctrl+Z', redo: 'Ctrl+Y'};

function History({model}: Props): ReactElement {
  const {history} = model;
  return (
    <>
      <Button
        size="sm"
        variant="ghost"
        icon="undo"
        title={`Undo (${SHORTCUTS.undo})`}
        disabled={!history.canUndo}
        onClick={history.undo}
      >
        Undo
      </Button>
      <Button
        size="sm"
        variant="ghost"
        icon="redo"
        title={`Redo (${SHORTCUTS.redo})`}
        disabled={!history.canRedo}
        onClick={history.redo}
      >
        Redo
      </Button>
    </>
  );
}

function Zoom({outline, manual}: Props): ReactElement {
  const flow = useReactFlow<CardNode, RouteEdgeType>();
  const zoom = useStore((store) => store.transform[2]);
  const act = (action: () => Promise<unknown>) => (): void => {
    manual.current = true;
    void action();
  };
  const fit = act(async () => flow.fitView(FIT_VIEW));
  return (
    <>
      <IconButton
        icon="zoom-out"
        label="Zoom out"
        disabled={outline}
        onClick={act(async () => flow.zoomOut())}
      />
      <span className="zoom-level" title="Zoom">
        {Math.round(zoom * 100)}%
      </span>
      <IconButton
        icon="zoom-in"
        label="Zoom in"
        disabled={outline}
        onClick={act(async () => flow.zoomIn())}
      />
      <IconButton icon="fit" label="Fit to screen" disabled={outline} onClick={fit} />
    </>
  );
}

/** Undo, Redo, Arrange, zoom, the outline and the connection style, floating over the canvas. */
export function CanvasToolbar(props: Props): ReactElement {
  return (
    <div className="canvas-toolbar" role="group" aria-label="Canvas tools">
      <History {...props} />
      <span className="toolbar-separator" />
      <Arrange
        document={props.model.document}
        catalog={props.catalog}
        onArrange={(placed) => {
          props.model.change((value) => ({...value, layout: {...value.layout, ...placed}}));
        }}
      />
      <span className="toolbar-separator" />
      <Zoom {...props} />
      <span className="toolbar-separator" />
      <Button
        size="sm"
        variant="ghost"
        icon="outline"
        pressed={props.outline}
        onClick={() => {
          props.onOutline(!props.outline);
        }}
      >
        Outline
      </Button>
      <ConnectionsMenu model={props.model} onPreview={props.onPreview} />
    </div>
  );
}
