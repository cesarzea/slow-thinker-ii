import type {ReactElement} from 'react';
import type {ModelProfile} from '../../api/index.ts';
import {SchemaField, SourceFields, sourceString} from '../../ui/index.ts';
import type {SourceValue} from '../../ui/index.ts';
import type {ComponentFormProps} from './types.ts';
interface Props extends ComponentFormProps {
  readonly path: string;
  readonly config: SourceValue;
  readonly profile: ModelProfile | undefined;
}
export function AgentModelFields(props: Props): ReactElement {
  const parameters = props.config.entries.get('parameters');
  const effort = parameters?.entries.get('reasoning_effort');
  const modelName =
    props.profile === undefined ? 'No discovered model profile' : props.profile.model;
  return (
    <>
      <p>Bound model: {modelName}. Validation and admission enforce its capabilities.</p>
      <SchemaField
        label="Reasoning effort"
        schema={{type: 'string', enum: props.profile?.reasoning_efforts ?? []}}
        source={effort}
        raw={effort?.raw}
        path={`${props.path}/config/parameters/reasoning_effort`}
        disabled={props.locked || parameters === undefined || props.profile === undefined}
        patch={props.patch}
      />
      <GenerationFields {...props} parameters={parameters} />
    </>
  );
}
function GenerationFields(
  props: Props & {readonly parameters: SourceValue | undefined},
): ReactElement {
  const path = `${props.path}/config/parameters`;
  const ceiling =
    props.profile === undefined ? 'unknown' : String(props.profile.maximum_output_tokens);
  const fields = [
    {
      label: `Maximum completion tokens (ceiling ${ceiling})`,
      path: `${path}/max_completion_tokens`,
      value: props.parameters?.entries.get('max_completion_tokens'),
    },
  ];
  const temperature = {
    label: 'Temperature',
    path: `${path}/temperature`,
    value: props.parameters?.entries.get('temperature'),
  };
  const disabled = props.locked || props.parameters === undefined;
  const temperatureDisabled = disabled || !supportsTemperature(props.profile, props.parameters);
  return (
    <>
      <SourceFields fields={fields} disabled={disabled} patch={props.patch} />
      <SourceFields fields={[temperature]} disabled={temperatureDisabled} patch={props.patch} />
    </>
  );
}

function supportsTemperature(
  profile: ModelProfile | undefined,
  parameters: SourceValue | undefined,
): boolean {
  return (
    profile?.supports_temperature === true &&
    ['', 'none'].includes(sourceString(parameters?.entries.get('reasoning_effort')))
  );
}
