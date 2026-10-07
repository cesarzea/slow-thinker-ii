import type {ReactElement, ReactNode} from 'react';
import type {Catalog, GraphDocument, OperatorClient} from '../../api/index.ts';
import type {CanvasObservation} from './canvas/observation-dot.tsx';
import {ObservationPanel} from './observation-panel.tsx';
import {observedModel, panelContext, useSession} from './run-mode-parts.ts';
import type {Shown} from './run-mode-parts.ts';
import type {Mode} from './run-mode-state.ts';
import {shownDocument, useExecuted} from './run-mode-state.ts';
import type {RenderRun, RunCounts} from './run-slot.ts';
import type {EditorModel} from './state/use-editor.ts';

export interface RunMode {
  readonly active: boolean;
  readonly enter: () => void;
  readonly leave: () => void;
  /** The document shown in run mode. */
  readonly document: GraphDocument;
  readonly counts: RunCounts;
  readonly observation: CanvasObservation;
  readonly left: ReactNode;
  readonly panel: ReactNode;
}

interface RunModeOptions {
  readonly client: OperatorClient;
  readonly editor: EditorModel;
  readonly catalog: Catalog;
  readonly renderRun: RenderRun | undefined;
  /** The run in the address, or null. */
  readonly routeRun: string | null;
  /** Puts the shown run in the address, or removes it. */
  readonly onRunChange: ((runId: string | null) => void) | undefined;
}

/** The observation points of what run mode shows. */
function Points(props: {
  readonly shown: Pick<Shown, 'document' | 'catalog' | 'session' | 'watched'>;
  readonly focus: Mode['focus'];
}): ReactElement {
  const {document, catalog, session, watched} = props.shown;
  return (
    <ObservationPanel
      document={document}
      catalog={catalog}
      observed={watched.observed}
      onObserve={watched.observe}
      focus={props.focus}
      onFocus={session.focus}
    />
  );
}

/**
 * Run mode: Run shows the observation points on the left and the run panel on the right
 * without executing; Execute runs what is on screen. A run opened from the runs list shows
 * the document it executed. Observed points are saved with the graph's view.
 */
export function useRunMode(options: RunModeOptions): RunMode {
  const {client, editor, catalog, renderRun} = options;
  const session = useSession(options.routeRun, options.onRunChange);
  const {mode} = session;
  const executed = useExecuted(client, mode?.runId ?? null);
  const document = shownDocument(editor.state.document, mode?.runId === null ? null : executed);
  const watched = observedModel(editor, catalog, document);
  const shown = {client, editor, catalog, document, session, watched};
  return {
    active: mode !== null,
    enter: () => {
      if (mode === null) session.show({runId: null, focus: null});
    },
    leave: () => {
      session.show(null);
    },
    document,
    counts: session.counts,
    observation: watched.observation,
    left: mode === null ? null : <Points shown={shown} focus={mode.focus} />,
    panel: mode === null || renderRun === undefined ? null : renderRun(panelContext(shown, mode)),
  };
}
