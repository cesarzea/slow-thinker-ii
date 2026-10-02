import type {ReactElement} from 'react';
import type {ExecutionPage, GraphDetail, ConfigurationCatalog} from '../../api/index.ts';
import {sourceTree, sourceString} from '../../ui/index.ts';
import type {SourceValue} from '../../ui/index.ts';
import {registeredType} from './source-config.ts';
interface Props {
  readonly source: string;
  readonly catalog: ConfigurationCatalog | null;
  readonly detail: GraphDetail | null;
  readonly activityDetail?: GraphDetail | null;
  readonly execution: ExecutionPage | null;
  readonly run: string | null;
}
export function ResourceInventory(props: Props): ReactElement {
  const components = sourceTree(props.source)?.entries.get('components');
  const resources = resourceIds(components, props.catalog, props.detail);
  return (
    <section aria-label="Experiment resource inventory">
      <h2>Resources and consumers</h2>
      <p>
        Sharing occurs only when consumers bind the same declared instance. Binding grants no
        authority.
      </p>
      {resources.length === 0 && (
        <p>No configured resource instances are reported for this draft.</p>
      )}
      {resources.map((id) => (
        <ResourceCard
          key={id}
          id={id}
          component={components?.entries.get(id)}
          consumers={consumers(components, id)}
        />
      ))}
      <RecordedResourceActivity {...props} />
    </section>
  );
}
function resourceIds(
  components: SourceValue | undefined,
  catalog: ConfigurationCatalog | null,
  detail: GraphDetail | null,
): string[] {
  return [...(components?.entries ?? [])]
    .filter(
      ([id, item]) =>
        registeredType(catalog, item)?.roles.includes('resource') === true ||
        detail?.structure.components.some(
          (item) => item.id === id && item.roles.includes('resource'),
        ) === true,
    )
    .map(([id]) => id);
}
function consumers(components: SourceValue | undefined, id: string): string[] {
  return [...(components?.entries ?? [])]
    .filter(([, component]) =>
      [...(component.entries.get('resources')?.entries.values() ?? [])].some(
        (target) => sourceString(target) === id,
      ),
    )
    .map(([name]) => name);
}
function ResourceCard(props: {
  readonly id: string;
  readonly component: SourceValue | undefined;
  readonly consumers: readonly string[];
}): ReactElement {
  const config = props.component?.entries.get('config');
  return (
    <article className="inventory-card">
      <h3>{props.id}</h3>
      <p>
        {sharingLabel(props.consumers.length)} · {props.consumers.join(', ') || 'No consumers'}
      </p>
      <ResourceMetadata config={config} />
    </article>
  );
}
function ResourceMetadata({config}: {readonly config: SourceValue | undefined}): ReactElement {
  const fields = [
    ['Retention', 'retention'],
    ['Namespace', 'namespace'],
    ['Model profile', 'provider_profile'],
  ];
  return (
    <>
      {fields.map(([label, key]) => (
        <p key={key}>
          {label}: {sourceString(config?.entries.get(key ?? '')) || 'Not configured'}
        </p>
      ))}
    </>
  );
}
function sharingLabel(count: number): string {
  if (count > 1) return 'Shared by selected consumers';
  return count === 1 ? 'One bound consumer' : 'Unbound instance';
}
function RecordedResourceActivity(props: Props): ReactElement {
  const resources = new Set(
    props.activityDetail?.structure.components
      .filter((item) => item.roles.includes('resource'))
      .map((item) => item.id),
  );
  const calls = props.execution?.calls.filter((call) => resources.has(call.target)) ?? [];
  return (
    <section aria-label="Recorded resource activity">
      <h3>Recorded activity {props.run ?? ''}</h3>
      <p>
        Activity uses the selected run's admitted resources; current draft bindings cannot alter it.
      </p>
      {props.execution === null ? (
        <p>Select a saved run to inspect recorded calls.</p>
      ) : (
        <ul>
          {calls.map((call) => (
            <li key={call.id}>
              {call.id}: {call.caller} → {call.target}.{call.operation} · {call.state}
            </li>
          ))}
        </ul>
      )}
      {props.execution !== null && calls.length === 0 && (
        <p>No resource calls are recorded in the loaded execution snapshot.</p>
      )}
    </section>
  );
}
