import type {ReactElement} from 'react';
import {ChoiceControl, SourceFields, sourceString, sourceTree} from '../../ui/index.ts';
import type {SourceValue} from '../../ui/index.ts';
import type {ComponentFormProps} from './types.ts';
import {registeredType} from './source-config.ts';
import {resolveSchema, schemaObject} from './schema-resolution.ts';
import {AgentModelFields} from './agent-model-fields.tsx';
interface Props extends ComponentFormProps {
  readonly path: string;
}
export function ModelFields(props: Props): ReactElement | null {
  const config = props.component.entries.get('config');
  if (config === undefined) return null;
  const descriptor = registeredType(props.catalog, props.component);
  const properties = schemaObject(
    resolveSchema(descriptor?.config_schema ?? {}, props.catalog?.schema_documents ?? {})[
      'properties'
    ],
  );
  if (Object.hasOwn(properties, 'provider_profile'))
    return (
      <ModelSelection {...props} profile={sourceString(config.entries.get('provider_profile'))} />
    );
  return Object.hasOwn(properties, 'instructions') ? (
    <PromptModelFields {...props} config={config} />
  ) : null;
}
function PromptModelFields(props: Props & {readonly config: SourceValue}): ReactElement {
  const target = sourceString(props.component.entries.get('resources')?.entries.get('model'));
  const modelConfig = sourceTree(props.source)
    ?.entries.get('components')
    ?.entries.get(target)
    ?.entries.get('config');
  const profile = props.catalog?.models.find(
    (item) => item.provider_profile === sourceString(modelConfig?.entries.get('provider_profile')),
  );
  const fields = [
    {
      label: 'Model parameters and extensions',
      path: `${props.path}/config/parameters`,
      value: props.config.entries.get('parameters'),
    },
    {
      label: 'Output format and schema',
      path: `${props.path}/config/output`,
      value: props.config.entries.get('output'),
    },
  ];
  return (
    <fieldset disabled={props.locked}>
      <legend>Model generation options</legend>
      <AgentModelFields {...props} profile={profile} />
      <SourceFields fields={fields} disabled={props.locked} patch={props.patch} />
    </fieldset>
  );
}
function ModelSelection(props: Props & {readonly profile: string}): ReactElement {
  const change = (profile: string): void => {
    const model = props.catalog?.models.find((item) => item.provider_profile === profile);
    if (model === undefined) return;
    void props.patch([
      {
        op: 'add',
        path: `${props.path}/config/provider_profile`,
        value_json: JSON.stringify(profile),
      },
      {op: 'add', path: `${props.path}/config/model`, value_json: JSON.stringify(model.model)},
    ]);
  };
  const choices =
    props.catalog?.models.map((model) => ({
      value: model.provider_profile,
      label: `${model.provider} · ${model.model} · ${model.tariff_status}`,
    })) ?? [];
  return (
    <>
      <ChoiceControl
        label="Model provider profile"
        value={props.profile}
        disabled={props.locked}
        onValue={change}
        choices={[{value: '', label: 'Choose a configured model'}, ...choices]}
      />
    </>
  );
}
