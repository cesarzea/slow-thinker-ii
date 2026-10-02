import {useState} from 'react';
import type {ReactElement} from 'react';
import {ChoiceControl, sourceTree} from '../../ui/index.ts';
import {ComponentForm} from './component-form.tsx';
import {NewInstance} from './new-instance.tsx';
import type {SourceWorkspaceProps} from './types.ts';

export function InstanceEditor(props: SourceWorkspaceProps): ReactElement {
  const components = sourceTree(props.source)?.entries.get('components');
  const ids = [...(components?.entries.keys() ?? [])];
  const [selected, select] = useState('');
  const id = ids.includes(selected) ? selected : (ids[0] ?? '');
  const component = components?.entries.get(id);
  return (
    <section aria-label="Component instances">
      <h2>Configure experiment components</h2>
      <ChoiceControl
        label="Component instance"
        value={id}
        onValue={select}
        choices={ids.map((name) => ({value: name, label: name}))}
      />
      {component !== undefined ? (
        <ComponentForm key={id} {...props} id={id} component={component} />
      ) : (
        <p>Add a registered component to this draft.</p>
      )}
      <NewInstance {...props} />
    </section>
  );
}
