import type {ReactElement} from 'react';
import type {GraphDocument} from '../../../api/index.ts';
import {Icon} from '../../../ui/index.ts';
import {setLimits} from '../state/document.ts';
import {LIMIT_FIELDS, graphNameProblem, parseLimit} from '../state/limits.ts';
import type {EditorModel} from '../state/use-editor.ts';
import {CommitField} from './commit-field.tsx';

type Update = (document: GraphDocument) => GraphDocument;

function RunLimits({editor}: {readonly editor: EditorModel}): ReactElement {
  const {limits} = editor.state.document;
  const change = (update: Update): void => {
    editor.dispatch({type: 'change', update});
  };
  return (
    <section className="inspector-section" aria-label="Run limits">
      <h3 className="panel-title">Run limits</h3>
      {LIMIT_FIELDS.map((field) => (
        <CommitField
          key={`${field.key}:${String(limits[field.key])}`}
          label={field.label}
          type={field.maximum === null ? 'text' : 'number'}
          value={String(limits[field.key])}
          check={(text) => parseLimit(field, text).problem}
          onCommit={(text) => {
            const {value} = parseLimit(field, text);
            if (value !== null)
              change((document) => setLimits(document, {...document.limits, [field.key]: value}));
          }}
        />
      ))}
      <p className="field-note">Daily and monthly budgets are platform settings for all runs.</p>
    </section>
  );
}

function GraphName({editor}: {readonly editor: EditorModel}): ReactElement {
  const {name} = editor.state.document;
  return (
    <section className="inspector-section" aria-label="Graph name">
      <CommitField
        key={name}
        label="Graph name"
        wide
        type="text"
        value={name}
        check={graphNameProblem}
        onCommit={(text) => {
          editor.dispatch({type: 'change', update: (value) => ({...value, name: text})});
        }}
      />
    </section>
  );
}

/** The graph itself when no node is selected: its name and the limits of every run. */
export function GraphInspector({editor}: {readonly editor: EditorModel}): ReactElement {
  return (
    <aside className="side-panel" aria-label="Graph">
      <header className="inspector-head">
        <span className="tile tile-neutral" aria-hidden="true">
          <Icon name="graph" />
        </span>
        <div className="inspector-titles">
          <h2>Graph</h2>
          <p className="inspector-sub">Settings of every run</p>
        </div>
      </header>
      <GraphName editor={editor} />
      <RunLimits editor={editor} />
      <p className="inspector-hint">Select a node to see its configuration and connections.</p>
    </aside>
  );
}
