import {useEffect, useRef} from 'react';
import type {ReactElement, RefObject} from 'react';
import {Controls, useReactFlow} from '@xyflow/react';
import type {FitViewOptions, ReactFlowProps} from '@xyflow/react';
import type {CardNode, RouteEdgeType} from './types.ts';

export type ManualViewport = RefObject<boolean>;
export type CanvasInteraction = ReturnType<typeof useCanvasInteraction>;
export const FIT_VIEW: FitViewOptions<CardNode> = {maxZoom: 1, padding: 0.2};

/** Remember when the person moved or zoomed the view, so resizing does not reframe it. */
export function useCanvasInteraction(): {
  readonly manual: ManualViewport;
  readonly events: Pick<ReactFlowProps<CardNode, RouteEdgeType>, 'onMoveStart' | 'onNodeDragStart'>;
} {
  const manual = useRef(false);
  return {
    manual,
    events: {
      onMoveStart: (event) => {
        if (event !== null) manual.current = true;
      },
      onNodeDragStart: () => {
        manual.current = true;
      },
    },
  };
}

export function CanvasControls({manualRef}: {readonly manualRef: ManualViewport}): ReactElement {
  const flow = useReactFlow<CardNode, RouteEdgeType>();
  const markManual = (): void => {
    manualRef.current = true;
  };
  return (
    <Controls
      showInteractive={false}
      onZoomIn={markManual}
      onZoomOut={markManual}
      onFitView={() => {
        markManual();
        void flow.fitView(FIT_VIEW);
      }}
    />
  );
}

/** Frame every node whenever nodes are added or removed, and on resize until moved by hand. */
export function CanvasFraming(props: {
  readonly count: number;
  readonly manualRef: ManualViewport;
}): null {
  const flow = useReactFlow<CardNode, RouteEdgeType>();
  const previous = useRef(props.count);
  const {count, manualRef} = props;
  useEffect(() => {
    if (previous.current === count) return;
    previous.current = count;
    void flow.fitView(FIT_VIEW);
  }, [count, flow]);
  useEffect(() => {
    const resize = (): void => {
      if (!manualRef.current) void flow.fitView(FIT_VIEW);
    };
    window.addEventListener('resize', resize);
    return () => {
      window.removeEventListener('resize', resize);
    };
  }, [flow, manualRef]);
  return null;
}
