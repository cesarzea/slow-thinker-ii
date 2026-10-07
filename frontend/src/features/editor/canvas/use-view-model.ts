import {useState} from 'react';
import type {GraphDocument} from '../../../api/index.ts';
import type {CanvasModel} from './canvas-model.ts';

/** How a run's graph is shown: the cards' positions and the connection view. */
interface Presentation {
  readonly layout: GraphDocument['layout'];
  readonly view: GraphDocument['view'];
}
interface Stack {
  readonly past: readonly Presentation[];
  readonly current: Presentation | null;
  readonly future: readonly Presentation[];
}

function shown(document: GraphDocument, current: Presentation | null): GraphDocument {
  if (current === null) return document;
  const {view} = current;
  return {...document, layout: current.layout, ...(view === undefined ? {} : {view})};
}

/** Undo and Redo over the presentations kept in the stack. */
function stackHistory(
  stack: Stack,
  presentation: Presentation,
  setStack: (stack: Stack) => void,
): CanvasModel['history'] {
  return {
    canUndo: stack.past.length > 0,
    canRedo: stack.future.length > 0,
    undo: () => {
      const previous = stack.past.at(-1);
      if (previous === undefined) return;
      const future = [presentation, ...stack.future];
      setStack({past: stack.past.slice(0, -1), current: previous, future});
    },
    redo: () => {
      const [next, ...rest] = stack.future;
      if (next === undefined) return;
      setStack({past: [...stack.past, presentation], current: next, future: rest});
    },
  };
}

/**
 * A run's graph arranged and styled in this view only, with local Undo and Redo: changes
 * keep the cards' positions and the connection view, never the graph itself.
 */
export function useViewModel(document: GraphDocument): CanvasModel {
  const [stack, setStack] = useState<Stack>({past: [], current: null, future: []});
  const current = shown(document, stack.current);
  const presentation = {layout: current.layout, view: current.view};
  return {
    document: current,
    change: (update) => {
      const next = update(current);
      const kept = {layout: next.layout, view: next.view};
      setStack({past: [...stack.past, presentation], current: kept, future: []});
    },
    history: stackHistory(stack, presentation, setStack),
  };
}
