import {useEffect, useState} from 'react';
import {DefinitionClient, OperatorClient} from '../api/index.ts';
import type {GraphDetail, GraphSummary} from '../api/index.ts';

interface DetailState {
  readonly detail: GraphDetail | null;
  readonly error: string | null;
  readonly context: string | null;
}
export function useGraphDetail(
  graph: GraphSummary,
  credential: string | undefined,
): Pick<DetailState, 'detail' | 'error'> {
  const [state, setState] = useState<DetailState>({detail: null, error: null, context: null});
  const context = JSON.stringify([credential, graph.graph_id, graph.revision]);
  useEffect(() => {
    const controller = new AbortController();
    void readDetail(graph, credential, controller.signal).then(
      (detail) => {
        if (!controller.signal.aborted) setState({detail, error: null, context});
      },
      () => {
        if (!controller.signal.aborted)
          setState({
            detail: null,
            error: 'Could not load the exact experiment definition.',
            context,
          });
      },
    );
    return () => {
      controller.abort();
    };
  }, [graph, credential, context]);
  return state.context === context ? state : {detail: null, error: null};
}

function readDetail(
  graph: GraphSummary,
  credential: string | undefined,
  signal: AbortSignal,
): Promise<GraphDetail> {
  return credential === undefined
    ? new OperatorClient('').graph(graph.graph_id, graph.revision, signal)
    : new DefinitionClient(credential).detail(
        {graph_id: graph.graph_id, revision: graph.revision},
        signal,
      );
}
