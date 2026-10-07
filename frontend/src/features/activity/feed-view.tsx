import {useState} from 'react';
import type {ReactElement} from 'react';
import type {RunEventKind} from '../../api/index.ts';

/**
 * What the Content view leaves out: a host starting, the run starting to run, and
 * activations starting and ending. What a node or connection carries stays, as chosen on
 * the left; All events shows everything, for debugging.
 */
export const LIFECYCLE: ReadonlySet<RunEventKind> = new Set<RunEventKind>([
  'host.ready',
  'run.running',
  'activation.started',
  'activation.completed',
  'activation.cancelled',
]);

export type View = 'content' | 'all';
const VIEW_KEY = 'slow-thinker-ii.observation-view';

function storedView(): View {
  try {
    return localStorage.getItem(VIEW_KEY) === 'all' ? 'all' : 'content';
  } catch {
    return 'content';
  }
}

/** Content, or every event for debugging; remembered in this browser when storage allows. */
export function useView(): [View, (view: View) => void] {
  const [view, setView] = useState<View>(storedView);
  return [
    view,
    (next) => {
      try {
        localStorage.setItem(VIEW_KEY, next);
      } catch {
        // The choice then lasts until the page is left.
      }
      setView(next);
    },
  ];
}

/** The choice between the Content view and every event. */
export function ViewChoice(props: {
  readonly view: View;
  readonly onChange: (view: View) => void;
}): ReactElement {
  return (
    <div className="feed-view" role="group" aria-label="Show">
      <button
        type="button"
        aria-pressed={props.view === 'content'}
        onClick={() => {
          props.onChange('content');
        }}
      >
        Content
      </button>
      <button
        type="button"
        aria-pressed={props.view === 'all'}
        onClick={() => {
          props.onChange('all');
        }}
      >
        All events
      </button>
    </div>
  );
}
