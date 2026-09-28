import {useEffect, useState} from 'react';
import {loadGraphs} from '../api/index.ts';
import type {GraphSummary} from '../api/index.ts';

interface CatalogState {
  graphs: GraphSummary[];
  error: string | null;
  loading: boolean;
}

export function useCatalog(credential?: string): CatalogState {
  const [state, setState] = useState<CatalogState>({graphs: [], error: null, loading: true});
  useEffect(() => {
    const controller = new AbortController();
    void loadGraphs(controller.signal, credential).then(
      (graphs) => {
        if (!controller.signal.aborted) setState({graphs, error: null, loading: false});
      },
      () => {
        if (!controller.signal.aborted) {
          setState({graphs: [], error: 'No se pudo cargar el catálogo.', loading: false});
        }
      },
    );
    return () => {
      controller.abort();
    };
  }, [credential]);
  return state;
}
