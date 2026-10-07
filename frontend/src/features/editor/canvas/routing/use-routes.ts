import {createContext, useContext, useMemo} from 'react';
import {useStore} from '@xyflow/react';
import type {ReactFlowState} from '@xyflow/react';
import type {ConnectionView} from '../connection-style.ts';
import type {RouteEdgeType} from '../types.ts';
import {edgeRoutes} from './edge-routes.ts';
import type {EdgeRoute} from './edge-routes.ts';
import {sameScene, sceneOf} from './scene.ts';
import type {Scene} from './scene.ts';

type Routes = ReadonlyMap<string, EdgeRoute>;

/** The canvas's routes by connection; each connection draws its own. */
export const RoutesContext = createContext<Routes>(new Map());

export function useEdgeRoute(id: string): EdgeRoute | undefined {
  return useContext(RoutesContext).get(id);
}

const selectScene = (state: ReactFlowState): Scene => sceneOf(state.nodeLookup.values());

/**
 * All connections drawn in the graph's view together, so that each port label keeps clear
 * of every route, card and handle; recomputed whenever a card or handle moves.
 */
export function useRoutes(edges: readonly RouteEdgeType[], view: ConnectionView): Routes {
  const scene = useStore(selectScene, sameScene);
  return useMemo(() => edgeRoutes(scene, edges, view), [scene, edges, view]);
}
