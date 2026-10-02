import {useEffect, useMemo, useSyncExternalStore} from 'react';
import {CatalogModel} from './catalog-model.ts';
import type {CatalogState} from './catalog-state.ts';

export function useCatalog(credential?: string): CatalogState & {readonly model: CatalogModel} {
  const model = useMemo(() => new CatalogModel(credential), [credential]);
  const state = useSyncExternalStore(model.subscribe, model.snapshot);
  useEffect(() => {
    void model.refresh();
    return model.dispose;
  }, [model]);
  return {...state, model};
}
