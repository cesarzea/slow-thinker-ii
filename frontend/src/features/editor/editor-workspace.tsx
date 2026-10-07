import {useEffect, useState} from 'react';
import type {ReactElement, ReactNode} from 'react';
import {EditorBody} from './editor-body.tsx';
import {EditorDialogs} from './editor-dialogs.tsx';
import type {OpenDialog} from './editor-dialogs.tsx';
import {EditorHeader} from './editor-header.tsx';
import type {EditorProps} from './editor-props.ts';
import type {HistoryContext} from './history.ts';
import {useRunMode} from './run-mode.tsx';
import type {RunMode} from './run-mode.tsx';
import {StatusBar} from './status-bar.tsx';
import type {EditorSource} from './state/load.ts';
import {useEditor} from './state/use-editor.ts';
import type {DraftModel, EditorModel} from './state/use-editor.ts';
import {useUndoKeys} from './state/use-undo-keys.ts';

export type WorkspaceProps = EditorProps & {
  readonly source: EditorSource;
  readonly onBranchChange: (name: string) => void;
  /** Kept by the editor, so that the history panel stays open across branches. */
  readonly historyOpen: boolean;
  readonly onHistory: (open: boolean) => void;
};

function useDraftRegistration(onDraft: WorkspaceProps['onDraft'], draft: DraftModel): void {
  useEffect(() => {
    onDraft?.(draft);
  });
  useEffect(
    () => () => {
      onDraft?.(null);
    },
    [onDraft],
  );
}

function historyContext(
  editor: EditorModel,
  props: WorkspaceProps,
  close: () => void,
): HistoryContext {
  const {target, stored, versions, refreshVersions} = editor.persistence;
  return {
    graphId: target.graphId,
    branch: target.branch,
    latestChange: stored?.change ?? null,
    activeVersion: versions.active,
    onRestore: (document) => {
      editor.dispatch({type: 'replace', document});
    },
    onBranchChange: props.onBranchChange,
    onActivated: () => {
      void refreshVersions();
    },
    onClose: close,
  };
}

function historyPanel(editor: EditorModel, props: WorkspaceProps): ReactNode {
  const close = (): void => {
    props.onHistory(false);
  };
  return props.historyOpen ? props.renderHistory?.(historyContext(editor, props, close)) : null;
}

/** Run mode for this editor: the run in the address, shown through the run panel slot. */
function useEditorRunMode(editor: EditorModel, props: WorkspaceProps): RunMode {
  return useRunMode({
    client: props.client,
    editor,
    catalog: props.source.catalog,
    renderRun: props.renderRun,
    routeRun: props.runId ?? null,
    onRunChange: props.onRunChange,
  });
}

/** The header's Edit and Run switch over run mode. */
function modeSwitch(run: RunMode) {
  return {running: run.active, onRunMode: run.enter, onEditMode: run.leave};
}

/** The editor: header, palette, canvas, inspector or history, status bar and dialogs. */
export function EditorWorkspace(props: WorkspaceProps): ReactElement {
  const editor = useEditor(props.client, props.source);
  const [dialog, setDialog] = useState<OpenDialog | null>(null);
  const run = useEditorRunMode(editor, props);
  useDraftRegistration(props.onDraft, editor.draft);
  useUndoKeys(editor.history);
  const {catalog} = props.source;
  return (
    <div className="editor">
      <EditorHeader {...props} editor={editor} {...modeSwitch(run)} />
      <EditorBody
        editor={editor}
        catalog={catalog}
        open={setDialog}
        history={historyPanel(editor, props)}
        run={run}
      />
      <StatusBar editor={editor} />
      <EditorDialogs
        dialog={dialog}
        editor={editor}
        client={props.client}
        catalog={catalog}
        close={() => {
          setDialog(null);
        }}
      />
    </div>
  );
}
