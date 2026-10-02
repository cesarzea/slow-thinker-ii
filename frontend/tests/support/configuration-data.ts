import bounded from '../../../docs/contracts/examples/bounded-flow.component.json';
import llm from '../../../docs/contracts/examples/llm-call.component.json';
import model from '../../../docs/contracts/examples/model.component.json';
import sequence from '../../../docs/contracts/examples/sequence.component.json';
import routed from '../../../docs/contracts/examples/routed-call.component.json';
import redirector from '../../../docs/contracts/examples/redirector.component.json';
import grounded from '../../../docs/contracts/examples/grounded-review.component.json';
import provider from '../../../components/model-provider/model-provider.component.json';
import calculator from '../../../components/calculator/calculator.component.json';
import memory from '../../../components/key-value-memory/key-value-memory.component.json';
import contextual from '../../../components/contextual-call/contextual-call.component.json';
import external from '../../../examples/resource-agent/resource-agent.component.json';
import graphSchema from '../../../docs/contracts/schemas/graph.schema.json';
import llmSchema from '../../../docs/contracts/schemas/llm-call-config.schema.json';
import metadata from './configuration-metadata.json';
import type {ConfigurationCatalog} from '../../src/api/index.ts';

// Metadata is captured from support.workspace_http's production catalogue projection.
// Descriptor/schema documents below remain canonical authored fixtures.
export const configuration: ConfigurationCatalog = {
  ...metadata,
  schema_version: '1',
  models: metadata.models.map((model) => ({...model, tariff_status: 'unavailable'})),
  components: [
    bounded,
    llm,
    model,
    sequence,
    routed,
    redirector,
    grounded,
    provider,
    calculator,
    memory,
    contextual,
    external,
  ].map((item) => ({
    type_id: item.type_id,
    type_version: item.type_version,
    roles: item.roles,
    config_schema: item.config_schema,
    resource_slots: item.resource_slots,
    operations: item.operations,
    installation_status: 'ready',
  })),
  graph_schema: graphSchema,
  schema_documents: {[llmSchema.$id]: llmSchema},
};
