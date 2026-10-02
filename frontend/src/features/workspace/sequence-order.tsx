import type {ReactElement} from 'react';
import {JsonField, sourceString} from '../../ui/index.ts';
import {controllerSource} from './source-config.ts';
import type {SourceValue} from '../../ui/index.ts';
import type {SourceWorkspaceProps} from './types.ts';
export function SequenceOrder(props: SourceWorkspaceProps & {readonly path: string}): ReactElement {
  const steps = controllerSource(props.source).config?.entries.get('steps');
  const reorder = (index: number, direction: number): void => {
    reorderSteps(props, steps, index, direction);
  };
  return (
    <>
      <ol aria-label="Sequence order">
        {steps?.items.map((item, index) => (
          <OrderedStep
            key={JSON.stringify([item.raw, index])}
            label={sourceString(item)}
            index={index}
            total={steps.items.length}
            locked={props.locked}
            reorder={reorder}
          />
        ))}
      </ol>
      <JsonField
        label="Sequence node order"
        path={`${props.path}/steps`}
        raw={steps?.raw}
        disabled={props.locked}
        patch={props.patch}
      />
    </>
  );
}
function OrderedStep(props: {
  readonly label: string;
  readonly index: number;
  readonly total: number;
  readonly locked: boolean;
  readonly reorder: (index: number, direction: number) => void;
}): ReactElement {
  return (
    <li>
      {props.label}
      <button
        disabled={props.locked || props.index === 0}
        onClick={() => {
          props.reorder(props.index, -1);
        }}
      >
        Move step {props.index + 1} up
      </button>
      <button
        disabled={props.locked || props.index === props.total - 1}
        onClick={() => {
          props.reorder(props.index, 1);
        }}
      >
        Move step {props.index + 1} down
      </button>
    </li>
  );
}

function reorderSteps(
  props: SourceWorkspaceProps & {readonly path: string},
  steps: SourceValue | undefined,
  index: number,
  direction: number,
): void {
  const values = steps?.items.map((item) => item.raw) ?? [];
  const current = values[index];
  const target = values[index + direction];
  if (current === undefined || target === undefined) return;
  values[index] = target;
  values[index + direction] = current;
  void props.patch([
    {op: 'replace', path: `${props.path}/steps`, value_json: `[${values.join(',')}]`},
  ]);
}
