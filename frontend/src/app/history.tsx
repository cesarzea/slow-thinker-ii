import type {ReactElement} from 'react';
import type {OperatorClient} from '../api/index.ts';
import {GraphPreview} from '../features/editor/index.ts';
import type {HistoryContext} from '../features/editor/index.ts';
import {HistoryPanel} from '../features/versions/index.ts';

const NO_COUNTS: Readonly<Record<string, number>> = {};

/** The editor's History panel, drawn by the versions feature with the editor's canvas. */
export function historyPanel(client: OperatorClient): (context: HistoryContext) => ReactElement {
  return function History(context) {
    return (
      <HistoryPanel
        {...context}
        client={client}
        renderGraph={(graph) => (
          <GraphPreview {...graph} activations={NO_COUNTS} messages={NO_COUNTS} />
        )}
      />
    );
  };
}
