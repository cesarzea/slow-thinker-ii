import type {CSSProperties, ReactElement, ReactNode} from 'react';
import type {Catalog, ComponentDeclaration} from '../../api/index.ts';
import {CanvasArea} from './canvas-area.tsx';
import {GraphPreview} from './canvas/graph-preview.tsx';
import type {OpenDialog} from './editor-dialogs.tsx';
import {Palette} from './palette.tsx';
import {Inspector} from './panel/inspector.tsx';
import type {RunMode} from './run-mode.tsx';
import {PanelResizer, PanelToggle, usePanelCollapsed, usePanelWidth} from './side-panel.tsx';
import {embedInto, insideOnly} from './state/embed-into.ts';
import type {EditorModel} from './state/use-editor.ts';

interface BodyProps {
  readonly editor: EditorModel;
  readonly catalog: Catalog;
  readonly open: (dialog: OpenDialog | null) => void;
  readonly history: ReactNode;
  readonly run: RunMode;
}

/** The editable canvas, or in run mode the shown run's graph with its counts and dots. */
function Canvas({editor, catalog, open, run}: BodyProps): ReactElement {
  if (!run.active) return <CanvasArea editor={editor} catalog={catalog} open={open} />;
  return (
    <div className="canvas-area">
      <GraphPreview
        document={run.document}
        catalog={catalog}
        activations={run.counts.activations}
        messages={run.counts.messages}
        observation={run.observation}
        arrangeable
      />
    </div>
  );
}

/** The right panel: the run panel in run mode, else the history or the inspector. */
function RightPanel(
  props: BodyProps & {readonly collapsed: boolean; readonly onExpand: () => void},
): ReactElement {
  if (props.collapsed)
    return <aside className="panel-rail" aria-label="Panel" onClick={props.onExpand} />;
  return <>{props.run.active ? props.run.panel : (props.history ?? <Inspector {...props} />)}</>;
}

/** Adds a palette component: as a node, or into the selected node when it goes inside one. */
function adder(editor: EditorModel, catalog: Catalog): (declaration: ComponentDeclaration) => void {
  return (declaration) => {
    if (insideOnly(declaration)) embedInto(editor, catalog, declaration, editor.state.selected);
    else editor.dispatch({type: 'add', declaration});
  };
}

/** Palette or observation points, canvas, and the right panel, each side collapsible. */
export function EditorBody(props: BodyProps): ReactElement {
  const {run, catalog} = props;
  const add = adder(props.editor, catalog);
  const [left, toggleLeft] = usePanelCollapsed('left');
  const [right, toggleRight] = usePanelCollapsed('right');
  const [width, setWidth] = usePanelWidth();
  return (
    <div
      className="editor-body"
      style={right ? undefined : ({'--right': `${String(width)}px`} as CSSProperties)}
      data-mode={run.active ? 'run' : 'edit'}
      data-left={left ? 'collapsed' : 'open'}
      data-right={right ? 'collapsed' : 'open'}
    >
      {run.active && !left ? (
        run.left
      ) : (
        <Palette catalog={catalog} onAdd={add} collapsed={left} onExpand={toggleLeft} />
      )}
      <div className="editor-main">
        <Canvas {...props} />
      </div>
      <RightPanel {...props} collapsed={right} onExpand={toggleRight} />
      <PanelToggle side="left" name="components" collapsed={left} onToggle={toggleLeft} />
      <PanelToggle side="right" name="panel" collapsed={right} onToggle={toggleRight} />
      {!right && <PanelResizer width={width} onResize={setWidth} />}
    </div>
  );
}
