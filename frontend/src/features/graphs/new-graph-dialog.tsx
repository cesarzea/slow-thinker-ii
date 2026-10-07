import {useState} from 'react';
import type {ReactElement, SubmitEvent} from 'react';
import {errorMessage} from '../../api/index.ts';
import {Dialog, TextControl} from '../../ui/index.ts';
import {graphId} from './graph-id.ts';

export interface NewGraph {
  readonly id: string;
  readonly name: string;
}
interface Props {
  readonly onCreate: (graph: NewGraph) => Promise<void>;
  readonly onCancel: () => void;
}

/** The problem with a name, or `null` for a name of 1 to 120 characters. */
function nameProblem(name: string): string | null {
  return name === '' || name.length > 120 ? 'Enter a name of 1 to 120 characters.' : null;
}

/** Asks for a graph name; the graph is created on the server at once. */
export function NewGraphDialog({onCreate, onCancel}: Props): ReactElement {
  const [name, setName] = useState('');
  const [problem, setProblem] = useState<string | null>(null);
  const submit = async (event: SubmitEvent): Promise<void> => {
    event.preventDefault();
    const trimmed = name.trim();
    const invalid = nameProblem(trimmed);
    if (invalid !== null) {
      setProblem(invalid);
      return;
    }
    await onCreate({id: graphId(trimmed), name: trimmed}).catch((error: unknown) => {
      setProblem(`The graph could not be created. ${errorMessage(error)}`);
    });
  };
  return (
    <Dialog title="New graph" onClose={onCancel}>
      <form className="dialog-form" onSubmit={(event) => void submit(event)}>
        <TextControl label="Name" value={name} onValue={setName} />
        {problem !== null && <p role="alert">{problem}</p>}
        <DialogButtons onCancel={onCancel} />
      </form>
    </Dialog>
  );
}

function DialogButtons({onCancel}: {readonly onCancel: () => void}): ReactElement {
  return (
    <div className="dialog-actions">
      <button type="button" onClick={onCancel}>
        Cancel
      </button>
      <button type="submit" className="primary">
        Create
      </button>
    </div>
  );
}
