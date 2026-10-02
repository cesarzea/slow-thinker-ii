import type {ReactElement} from 'react';
import type {ConfigurationCatalog, InstalledType, ModelProfile} from '../../api/index.ts';
export function ComponentInventory({
  catalog,
}: {
  readonly catalog: ConfigurationCatalog | null;
}): ReactElement {
  return (
    <section aria-label="Installed component inventory">
      <h2>Registered component types</h2>
      <p>
        Reusable trusted installations are distinct from experiment instances. Discovery does not
        install or invoke a package.
      </p>
      {catalog === null ? (
        <p>Connect and load configuration discovery to see installed types.</p>
      ) : (
        <InstalledTypes types={catalog.components} />
      )}
    </section>
  );
}
function InstalledTypes({types}: {readonly types: readonly InstalledType[]}): ReactElement {
  if (types.length === 0) return <p>No component types are registered.</p>;
  return (
    <div className="trace-table">
      <table>
        <thead>
          <tr>
            <th>Type and version</th>
            <th>Roles</th>
            <th>Installation</th>
            <th>Operations</th>
          </tr>
        </thead>
        <tbody>
          {types.map((item) => (
            <InstalledRow key={JSON.stringify([item.type_id, item.type_version])} item={item} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
function InstalledRow({item}: {readonly item: InstalledType}): ReactElement {
  return (
    <tr>
      <td>
        {item.type_id}
        <br />
        {item.type_version}
      </td>
      <td>{item.roles.join(', ') || 'No roles reported'}</td>
      <td>{item.installation_status}</td>
      <td>{Object.keys(item.operations).join(', ') || 'No operations reported'}</td>
    </tr>
  );
}
export function ModelInventory({
  catalog,
}: {
  readonly catalog: ConfigurationCatalog | null;
}): ReactElement {
  return (
    <section aria-label="Configured models">
      <h2>Configured model profiles</h2>
      <p>
        Credentials and endpoints are managed by the server. Tariff readiness does not promise a
        successful provider call.
      </p>
      {catalog?.models.map((model) => (
        <ModelCard key={model.provider_profile} model={model} />
      ))}
      {catalog?.models.length === 0 && <p>No model profiles are configured.</p>}
    </section>
  );
}
function ModelCard({model}: {readonly model: ModelProfile}): ReactElement {
  return (
    <article className="inventory-card">
      <h3>{model.provider_profile}</h3>
      <p>
        {model.provider} · {model.model} · {model.tariff_status}
      </p>
      <p>Reasoning: {model.reasoning_efforts.join(', ') || 'No reasoning options reported'}</p>
      <p>
        Output tokens: {model.default_output_tokens} default · {model.maximum_output_tokens} maximum
      </p>
      <p>Temperature: {model.supports_temperature ? 'Supported' : 'Unsupported'}</p>
      <p>Reviewed until {reviewDate(model.review_expires_at)}</p>
    </article>
  );
}
function reviewDate(epoch: number): string {
  const date = new Date(epoch * 1000);
  return Number.isNaN(date.getTime()) ? 'Unavailable' : date.toISOString();
}
