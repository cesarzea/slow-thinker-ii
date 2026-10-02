import type {GraphReference, GraphSummary, ConfigurationCatalog} from '../api/index.ts';
import type {ExecutionObservation} from '../features/execution/index.ts';
import type {WorkspacePage} from './workspace-navigation.tsx';
export interface ExperimentExecutionProps {
  readonly credential: string;
  readonly graph: GraphSummary;
  readonly onSaved: (reference: GraphReference) => void;
  readonly onObservation: (observation: ExecutionObservation) => void;
  readonly onInspect: (run: string) => void;
  readonly selectionBlocked: boolean;
  readonly page?: WorkspacePage;
  readonly catalog?: ConfigurationCatalog | null;
  readonly observation?: ExecutionObservation;
  readonly onReadiness?: (state: ExperimentReadiness) => void;
}

export interface ExperimentReadiness {
  readonly key: string;
  readonly graph: GraphSummary;
  readonly blocked: boolean;
  readonly error: string | null;
  readonly reason: string | null;
}
