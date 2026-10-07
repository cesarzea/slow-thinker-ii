import {useId} from 'react';
import type {ReactElement} from 'react';
import type {Branch} from '../../api/index.ts';

interface BranchBarProps {
  readonly branches: readonly Branch[];
  readonly branch: string;
  readonly busy: boolean;
  readonly onChange: (name: string) => void;
  readonly onNew: () => void;
}

function BranchSelect(props: BranchBarProps): ReactElement {
  const id = useId();
  const names = props.branches.map((branch) => branch.name);
  const choices = names.includes(props.branch) ? names : [props.branch, ...names];
  return (
    <div className="branch-select">
      <label htmlFor={id}>Branch</label>
      <select
        id={id}
        value={props.branch}
        onChange={(event) => {
          props.onChange(event.target.value);
        }}
      >
        {choices.map((name) => (
          <option key={name} value={name}>
            {name}
          </option>
        ))}
      </select>
    </div>
  );
}

/** The branch the editor shows, and the start of a new one. */
export function BranchBar(props: BranchBarProps): ReactElement {
  return (
    <div className="branch-bar">
      <BranchSelect {...props} />
      <button type="button" className="small" disabled={props.busy} onClick={props.onNew}>
        New branch
      </button>
    </div>
  );
}
