import {useEffect, useState} from 'react';
import {OperatorClient} from '../api/index.ts';
import type {GraphDetail, GraphSummary} from '../api/index.ts';

interface DetailState {
  readonly detail: GraphDetail | null;
  readonly error: string | null;
}
export function useGraphDetail(graph: GraphSummary, credential: string | undefined): DetailState {
  const [state, setState] = useState<DetailState>({detail: null, error: null});
  useEffect(() => {
    const controller = new AbortController();
    void new OperatorClient(credential ?? '')
      .graph(graph.graph_id, graph.revision, controller.signal)
      .then(
        (detail) => {
          if (!controller.signal.aborted) setState({detail, error: null});
        },
        () => {
          if (!controller.signal.aborted)
            setState({
              detail: null,
              error: 'No se pudo cargar la definición exacta del experimento.',
            });
        },
      );
    return () => {
      controller.abort();
    };
  }, [graph.graph_id, graph.revision, credential]);
  return state.detail?.graph_id === graph.graph_id && state.detail.revision === graph.revision
    ? state
    : {detail: null, error: state.error};
}
