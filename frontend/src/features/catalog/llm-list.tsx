import {useId} from 'react';
import type {ReactElement} from 'react';
import type {LlmEntry} from '../../api/index.ts';
import {Facts} from './component-list.tsx';
import {parameterRows} from './llm-parameters.ts';

function ParameterTable({llm}: {readonly llm: LlmEntry}): ReactElement {
  const rows = parameterRows(llm.parameters);
  if (rows.length === 0) return <p className="catalog-description">No parameters.</p>;
  return (
    <table className="data-table catalog-parameters">
      <caption>Parameters</caption>
      <thead>
        <tr>
          <th scope="col">Parameter</th>
          <th scope="col">Range</th>
          <th scope="col">Default</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.name}>
            <th scope="row">{row.title}</th>
            <td>{row.range}</td>
            <td>{row.initial}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function LlmCard({llm}: {readonly llm: LlmEntry}): ReactElement {
  const id = useId();
  return (
    <li className="catalog-card" aria-labelledby={id}>
      <h3 id={id}>{llm.label}</h3>
      <Facts
        facts={[
          ['Provider', llm.provider],
          ['Identifier', llm.id],
        ]}
      />
      <ParameterTable llm={llm} />
    </li>
  );
}

/** The LLMs offered to graphs, with their parameters. */
export function LlmList({llms}: {readonly llms: readonly LlmEntry[]}): ReactElement {
  if (llms.length === 0) return <p className="empty-state">No LLMs are configured.</p>;
  return (
    <ul className="catalog-cards">
      {llms.map((llm) => (
        <LlmCard key={llm.id} llm={llm} />
      ))}
    </ul>
  );
}
