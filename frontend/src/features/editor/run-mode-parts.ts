import {useState} from 'react';
import {documentPoints} from '../../api/index.ts';
import type {Catalog, GraphDocument, OperatorClient, PointId} from '../../api/index.ts';
import type {CanvasObservation} from './canvas/observation-dot.tsx';
import {focusedPoints, pointLabels} from './observation-points.ts';
import {observedPoints, prepare, runBlock, useRouteRun} from './run-mode-state.ts';
import type {Mode} from './run-mode-state.ts';
import {asksForMessage, triggerMessage} from './run-request.ts';
import type {RunCounts, RunPanelContext} from './run-slot.ts';
import type {EditorModel} from './state/use-editor.ts';

const NO_COUNTS: RunCounts = {activations: {}, messages: {}};

/** Run mode's state: what it shows and the shown run's counts, kept in the address. */
export interface Session {
  readonly mode: Mode | null;
  readonly counts: RunCounts;
  readonly setCounts: (counts: RunCounts) => void;
  readonly show: (next: Mode | null) => void;
  readonly focus: (id: PointId | null) => void;
}

export function useSession(
  routeRun: string | null,
  onRunChange: ((runId: string | null) => void) | undefined,
): Session {
  const [mode, setMode] = useState<Mode | null>(null);
  const [counts, setCounts] = useState<RunCounts>(NO_COUNTS);
  useRouteRun(routeRun, mode, setMode);
  const show = (next: Mode | null): void => {
    setCounts(NO_COUNTS);
    setMode(next);
    const runId = next?.runId ?? null;
    if (runId !== (mode?.runId ?? null)) onRunChange?.(runId);
  };
  const focus = (id: PointId | null): void => {
    if (mode !== null) setMode({...mode, focus: id});
  };
  return {mode, counts, setCounts, show, focus};
}

/** The observed points, saved with the working copy's view when the choice changes. */
export interface Observed {
  readonly observed: ReadonlySet<PointId>;
  readonly observe: (ids: readonly PointId[], on: boolean) => void;
  readonly observation: CanvasObservation;
}

export function observedModel(
  editor: EditorModel,
  catalog: Catalog,
  document: GraphDocument,
): Observed {
  const observed = observedPoints(document, catalog);
  const observe = (ids: readonly PointId[], on: boolean): void => {
    const next = new Set(observed);
    for (const id of ids) {
      if (on) next.add(id);
      else next.delete(id);
    }
    const working = editor.state.document;
    const known = new Set([
      ...documentPoints(document, catalog),
      ...documentPoints(working, catalog),
    ]);
    const list = [...known].filter((id) => next.has(id));
    editor.dispatch({
      type: 'change',
      update: (value) => ({...value, view: {...value.view, observe: list}}),
    });
  };
  const toggle = (id: PointId): void => {
    observe([id], !observed.has(id));
  };
  return {observed, observe, observation: {observed, toggle}};
}

/** What run mode shows, and what it needs to show it. */
export interface Shown {
  readonly client: OperatorClient;
  readonly editor: EditorModel;
  readonly catalog: Catalog;
  readonly document: GraphDocument;
  readonly session: Session;
  readonly watched: Observed;
}

/** The points the run panel shows: every observed one, or what the focus stands for. */
function shownPoints({catalog, document, watched}: Shown, mode: Mode): PointId[] {
  return mode.focus === null ? [...watched.observed] : focusedPoints(mode.focus, document, catalog);
}

/** What the run panel knows of run mode, and what it can ask of it. */
export function panelContext(shown: Shown, mode: Mode): RunPanelContext {
  const {client, editor, catalog, document, session} = shown;
  const working = editor.state.document;
  return {
    graphId: editor.persistence.target.graphId,
    graphName: document.name,
    runId: mode.runId,
    message: triggerMessage(working),
    ask: asksForMessage(working),
    limits: document.limits,
    blocked: runBlock(editor),
    prepare: async () => prepare(client, editor),
    onStarted: (runId) => {
      session.show({runId, focus: null});
    },
    onReset: () => {
      session.show({runId: null, focus: null});
    },
    points: shownPoints(shown, mode),
    focus: mode.focus,
    onClearFocus: () => {
      session.focus(null);
    },
    labels: pointLabels(document, catalog),
    onCounts: session.setCounts,
    onClose: () => {
      session.show(null);
    },
  };
}
