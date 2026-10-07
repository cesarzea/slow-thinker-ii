import type {ReactElement} from 'react';
import {Button, ButtonLink, Icon} from '../../ui/index.ts';
import type {EditorProps} from './editor-props.ts';
import {
  activationBlock,
  activeText,
  canOfferActivation,
  pendingText,
  saveText,
} from './state/status.ts';
import type {EditorModel} from './state/use-editor.ts';

type HeaderProps = EditorProps & {
  readonly editor: EditorModel;
  readonly historyOpen: boolean;
  readonly onHistory: (open: boolean) => void;
  readonly running: boolean;
  readonly onRunMode: () => void;
  readonly onEditMode: () => void;
};

function Title({editor, graphsHref}: HeaderProps): ReactElement {
  const {persistence} = editor;
  const {active} = persistence.versions;
  return (
    <div className="editor-title">
      {graphsHref === undefined ? (
        <span className="crumb">Graphs</span>
      ) : (
        <a className="crumb" href={graphsHref}>
          Graphs
        </a>
      )}
      <span className="crumb" aria-hidden="true">
        /
      </span>
      <h1>{editor.state.document.name}</h1>
      <span className="branch-chip" title="Branch; switch branches in History">
        <Icon name="branch" size={12} />
        {persistence.target.branch}
      </span>
      <span className={active === null ? 'version-badge inactive' : 'version-badge'}>
        {activeText(persistence)}
      </span>
    </div>
  );
}

/** Saving, how far the working copy is from the active version, and activation problems. */
function SaveStatus({editor}: {readonly editor: EditorModel}): ReactElement {
  const {persistence} = editor;
  const failed = persistence.status.kind === 'failed';
  const pending = pendingText(persistence);
  const activation = persistence.activationFailure;
  return (
    <div className="save-line">
      <p role="status" className={failed ? 'save-status failed' : 'save-status'}>
        <Icon name={failed ? 'alert' : 'tick'} size={14} />
        {saveText(persistence)}
        {pending !== null && <span className="pending"> · {pending}</span>}
        {activation !== null && <span className="failed"> · Not activated: {activation}</span>}
      </p>
      {failed && (
        <Button size="sm" variant="ghost" onClick={() => void persistence.flush()}>
          Try again
        </Button>
      )}
    </div>
  );
}

function Activate({editor}: {readonly editor: EditorModel}): ReactElement | null {
  const {persistence, state} = editor;
  if (!canOfferActivation(persistence)) return null;
  const block = activationBlock(state, persistence);
  return (
    <Button
      variant="accent"
      disabled={block !== null}
      {...(block === null ? {} : {title: block})}
      onClick={() => void persistence.activate()}
    >
      Activate as v{persistence.versions.next}
    </Button>
  );
}

/** Edit or Run: run mode shows the observation points and the run panel; Execute runs. */
function ModeSwitch(props: HeaderProps): ReactElement {
  return (
    <div className="mode-switch" role="group" aria-label="Mode">
      <Button icon="edit" pressed={!props.running} onClick={props.onEditMode}>
        Edit
      </Button>
      <Button
        icon="play"
        pressed={props.running}
        title="Run mode: choose what to observe, then execute"
        onClick={props.onRunMode}
      >
        Run
      </Button>
    </div>
  );
}

/** Breadcrumb, active version, saving; History, Runs, Activate and Run. */
export function EditorHeader(props: HeaderProps): ReactElement {
  const stored = props.editor.persistence.stored !== null;
  return (
    <header className="editor-header">
      <Title {...props} />
      <SaveStatus editor={props.editor} />
      <div className="editor-actions">
        {props.renderHistory !== undefined && stored && (
          <Button
            icon="history"
            pressed={props.historyOpen}
            onClick={() => {
              props.onHistory(!props.historyOpen);
            }}
          >
            History
          </Button>
        )}
        {props.runsHref !== undefined && (
          <ButtonLink href={props.runsHref} icon="runs">
            Runs
          </ButtonLink>
        )}
        <Activate editor={props.editor} />
        <ModeSwitch {...props} />
      </div>
    </header>
  );
}
