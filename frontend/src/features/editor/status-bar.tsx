import {useId, useState} from 'react';
import type {ReactElement} from 'react';
import {Button, Icon} from '../../ui/index.ts';
import {storedText} from './state/status.ts';
import type {EditorModel} from './state/use-editor.ts';

const plural = (count: number, word: string): string =>
  `${String(count)} ${word}${count === 1 ? '' : 's'}`;

/** Every diagnostic of the graph; choosing one selects its node. */
function ProblemList(props: {readonly editor: EditorModel; readonly id: string}): ReactElement {
  const {editor, id} = props;
  const {document, diagnostics} = editor.state;
  const name = (nodeId: string | null): string =>
    document.nodes.find((node) => node.id === nodeId)?.name ?? 'Graph';
  const select = (nodeId: string | null): void => {
    if (nodeId !== null) editor.dispatch({type: 'select', nodeId});
  };
  return (
    <ul id={id} className="problem-list" aria-label="Problems">
      {diagnostics.map((item) => (
        <li key={`${item.code}:${item.path}:${item.message}`} className={item.severity}>
          <button
            type="button"
            onClick={() => {
              select(item.node_id);
            }}
          >
            <span className="severity">{item.severity === 'error' ? 'Error' : 'Warning'}</span>
            <span className="problem-node">{name(item.node_id)}</span>
            <span>{item.message}</span>
          </button>
        </li>
      ))}
    </ul>
  );
}

function ProblemsButton({editor}: {readonly editor: EditorModel}): ReactElement {
  const [open, setOpen] = useState(false);
  const list = useId();
  return (
    <span className="status-problems">
      <Button
        size="sm"
        variant="ghost"
        icon="alert"
        expanded={open}
        controls={list}
        onClick={() => {
          setOpen(!open);
        }}
      >
        {plural(editor.state.diagnostics.length, 'problem')}
      </Button>
      {open && <ProblemList editor={editor} id={list} />}
    </span>
  );
}

function CheckFailure({editor}: {readonly editor: EditorModel}): ReactElement {
  return (
    <span className="status-problems failed">
      <Icon name="alert" size={14} />
      Could not check the graph: {editor.state.checkFailure}
      <Button size="sm" variant="ghost" onClick={editor.recheck}>
        Check again
      </Button>
    </span>
  );
}

/** Whether the graph was checked, and its problems behind a button. */
function Problems({editor}: {readonly editor: EditorModel}): ReactElement {
  const {state} = editor;
  if (state.checkFailure !== null) return <CheckFailure editor={editor} />;
  const checking = state.checked !== state.revision;
  return (
    <>
      {state.diagnostics.length > 0 ? (
        <ProblemsButton editor={editor} />
      ) : (
        <span className={checking ? 'status-problems' : 'status-problems ok'}>
          <Icon name="check" size={14} />
          {checking ? 'Checking…' : 'No problems'}
        </span>
      )}
      {checking && state.diagnostics.length > 0 && <span className="checking">Checking…</span>}
    </>
  );
}

/** What was just undone, redone or deleted, with Undo when it can be undone. */
function Notice({editor}: {readonly editor: EditorModel}): ReactElement {
  const {notice, undo} = editor.history;
  return (
    <span className="status-notice" aria-live="polite">
      {notice?.text}
      {notice?.undo === true && (
        <>
          {' · '}
          <button
            type="button"
            className="link-button"
            aria-label={`Undo: ${notice.text}`}
            onClick={undo}
          >
            Undo
          </button>
        </>
      )}
    </span>
  );
}

/** Problems and counts on the left; notices; the latest saved change on the right. */
export function StatusBar({editor}: {readonly editor: EditorModel}): ReactElement {
  const {document} = editor.state;
  return (
    <footer className="status-bar">
      <Problems editor={editor} />
      <span>
        {plural(document.nodes.length, 'node')} ·{' '}
        {plural(document.connections.length, 'connection')}
      </span>
      <Notice editor={editor} />
      <span className="status-saved">{storedText(editor.persistence)}</span>
    </footer>
  );
}
