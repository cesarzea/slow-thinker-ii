import type {ReactElement, ReactNode} from 'react';
import type {ConnectionView} from './connection-style.ts';
import {EdgeRemoval} from './edge-selection.ts';
import {NodeActionsContext} from './node-actions.ts';
import type {NodeActions} from './node-actions.ts';
import {PortTipContext} from './port-tip.tsx';
import type {usePortTips} from './port-tip.tsx';
import {RoutesContext, useRoutes} from './routing/use-routes.ts';
import type {RouteEdgeType} from './types.ts';

/** What cards and connections read from their canvas: routes, port tips and removal. */
export function CanvasContexts(props: {
  readonly edges: RouteEdgeType[];
  readonly view: ConnectionView;
  readonly tips: ReturnType<typeof usePortTips>['tips'];
  readonly remove: ((edgeId: string) => void) | null;
  readonly actions: NodeActions | null;
  readonly children: ReactNode;
}): ReactElement {
  const routes = useRoutes(props.edges, props.view);
  return (
    <RoutesContext value={routes}>
      <PortTipContext value={props.tips}>
        <NodeActionsContext value={props.actions}>
          <EdgeRemoval value={props.remove}>{props.children}</EdgeRemoval>
        </NodeActionsContext>
      </PortTipContext>
    </RoutesContext>
  );
}
