import type {ReactElement} from 'react';
import type {Catalog, GraphNode, JsonObject} from '../../../api/index.ts';
import {
  ConfigurationField,
  fieldVisible,
  readPointer,
  schemaAt,
  writePointer,
} from '../../../ui/index.ts';
import {sectionConfig} from './sections.ts';
import type {NodeSection} from './sections.ts';

interface Props {
  readonly entry: NodeSection;
  readonly node: GraphNode;
  readonly catalog: Catalog;
  readonly onConfig: (config: JsonObject) => void;
}

/** The visible fields of one section, each bound to its configuration pointer. */
export function SectionFields({entry, node, catalog, onConfig}: Props): ReactElement {
  const config = sectionConfig(node, entry);
  const columns = entry.section.columns === 2 ? ' columns-2' : '';
  return (
    <div className={`section-form${columns}`}>
      {entry.section.fields
        .filter((field) => fieldVisible(field, config))
        .map((field) => (
          <ConfigurationField
            key={`${entry.key}:${field.path}`}
            field={field}
            schema={schemaAt(entry.declaration.config_schema, field.path)}
            value={readPointer(config, field.path)}
            services={catalog.llms}
            onChange={(value) => {
              onConfig(writePointer(config, field.path, value));
            }}
          />
        ))}
    </div>
  );
}
