import {useState} from 'react';
import type {ReactElement} from 'react';
import type {GraphReference} from '../../api/index.ts';
import {locked} from './draft.ts';
import type {EditorModel} from './types.ts';

interface Props {
  readonly reference: GraphReference;
  readonly model: EditorModel;
}

export function RevisionDraft({reference, model}: Props): ReactElement {
  const [graphId, setGraphId] = useState(reference.graph_id);
  const [revision, setRevision] = useState(
    () => `${reference.revision}-personal-${crypto.randomUUID()}`,
  );
  return (
    <fieldset disabled={locked(model.state) || model.dirty}>
      <legend>New revision or variant</legend>
      <p>
        Copy the selected saved definition. Keep its graph ID for a new revision, or change it for a
        variant. The exact source is recorded in derived_from.
      </p>
      <RevisionFields
        graphId={graphId}
        revision={revision}
        setGraphId={setGraphId}
        setRevision={setRevision}
      />
      <button
        disabled={!graphId || !revision}
        onClick={() => {
          void model.derive(graphId, revision);
        }}
      >
        Create draft from saved definition
      </button>
    </fieldset>
  );
}

function RevisionFields(props: {
  readonly graphId: string;
  readonly revision: string;
  readonly setGraphId: (value: string) => void;
  readonly setRevision: (value: string) => void;
}): ReactElement {
  return (
    <>
      <label>
        Graph ID
        <input
          value={props.graphId}
          onChange={(event) => {
            props.setGraphId(event.target.value);
          }}
        />
      </label>
      <label>
        New revision
        <input
          value={props.revision}
          onChange={(event) => {
            props.setRevision(event.target.value);
          }}
        />
      </label>
    </>
  );
}
