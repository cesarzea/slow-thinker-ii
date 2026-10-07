import {useState} from 'react';
import type {ReactElement, SubmitEvent} from 'react';
import type {BranchOrigin, ChangeSummary, VersionSummary} from '../../api/index.ts';
import {ChoiceControl, Dialog, TextControl} from '../../ui/index.ts';
import {BRANCH_NAME} from './actions.ts';
import {shortTime} from './times.ts';

export interface BranchDialogProps {
  readonly versions: readonly VersionSummary[];
  /** The open branch's changes, newest first. */
  readonly changes: readonly ChangeSummary[];
  readonly origin: BranchOrigin;
  readonly onCreate: (name: string, origin: BranchOrigin) => Promise<string | null>;
  readonly onCancel: () => void;
}

const INVALID_NAME =
  'Use 1 to 40 letters, digits, spaces, dots, underscores or hyphens, starting with a letter or digit.';

function originValue(origin: BranchOrigin): string {
  return 'version' in origin
    ? `version:${String(origin.version)}`
    : `change:${String(origin.change)}`;
}

function parseOrigin(value: string): BranchOrigin {
  const [kind, number = '0'] = value.split(':');
  return kind === 'version' ? {version: Number(number)} : {change: Number(number)};
}

function originChoices(props: BranchDialogProps): {value: string; label: string}[] {
  const versions = props.versions
    .toSorted((a, b) => b.version - a.version)
    .map((version) => ({
      value: originValue({version: version.version}),
      label: `Version ${String(version.version)} (${version.branch})`,
    }));
  const changes = props.changes.map((change) => ({
    value: originValue({change: change.change}),
    label: `Change ${String(change.change)} · ${shortTime(change.at)}`,
  }));
  return [...versions, ...changes];
}

function DialogButtons({onCancel}: {readonly onCancel: () => void}): ReactElement {
  return (
    <div className="dialog-actions">
      <button type="button" onClick={onCancel}>
        Cancel
      </button>
      <button type="submit" className="primary">
        Create branch
      </button>
    </div>
  );
}

/** Names a new branch and chooses the version or change it starts from. */
export function BranchDialog(props: BranchDialogProps): ReactElement {
  const [name, setName] = useState('');
  const [origin, setOrigin] = useState(originValue(props.origin));
  const [problem, setProblem] = useState<string | null>(null);
  const submit = async (event: SubmitEvent): Promise<void> => {
    event.preventDefault();
    const trimmed = name.trim();
    if (BRANCH_NAME.test(trimmed)) setProblem(await props.onCreate(trimmed, parseOrigin(origin)));
    else setProblem(INVALID_NAME);
  };
  const choices = originChoices(props);
  return (
    <Dialog title="New branch" onClose={props.onCancel}>
      <form className="dialog-form" onSubmit={(event) => void submit(event)}>
        <TextControl label="Name" value={name} onValue={setName} />
        <ChoiceControl label="Start from" value={origin} onValue={setOrigin} choices={choices} />
        {problem !== null && <p role="alert">{problem}</p>}
        <DialogButtons onCancel={props.onCancel} />
      </form>
    </Dialog>
  );
}
