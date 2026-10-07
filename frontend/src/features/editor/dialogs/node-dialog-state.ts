import {useState} from 'react';
import type {Dispatch, SetStateAction} from 'react';
import {errorMessage} from '../../../api/index.ts';
import type {
  Catalog,
  Diagnostic,
  GraphDocument,
  GraphNode,
  OperatorClient,
} from '../../../api/index.ts';
import {removeEmbedded} from '../state/embedding.ts';
import {declarationFor} from '../state/ports.ts';
import type {EmbeddedPosition} from '../state/ports.ts';

export interface NodeDialogProps {
  readonly client: OperatorClient;
  readonly document: GraphDocument;
  readonly catalog: Catalog;
  readonly nodeId: string;
  readonly section: string;
  readonly onApplied: (document: GraphDocument, diagnostics: Diagnostic[]) => void;
  readonly onCancel: () => void;
}
export interface NodeDialogState {
  readonly working: GraphDocument;
  readonly setWorking: Dispatch<SetStateAction<GraphDocument>>;
  readonly tab: string;
  readonly setTab: (tab: string) => void;
  /** The position of the embedded component being removed, or null. */
  readonly removing: EmbeddedPosition | null;
  readonly setRemoving: (removing: EmbeddedPosition | null) => void;
  readonly problems: readonly Diagnostic[];
  readonly failure: string | null;
  readonly apply: () => Promise<void>;
  readonly remove: () => void;
}

export const problemKey = (item: Diagnostic): string => `${item.code}|${item.path}|${item.message}`;

/** Errors on the node that the dialog's changes would introduce. */
function introducedErrors(
  before: readonly Diagnostic[],
  after: readonly Diagnostic[],
  nodeId: string,
): Diagnostic[] {
  const known = new Set(before.map(problemKey));
  return after.filter(
    (item) => item.severity === 'error' && item.node_id === nodeId && !known.has(problemKey(item)),
  );
}

export function embeddedLabel(node: GraphNode, catalog: Catalog): string | null {
  const labels = (node.embedded ?? []).map(
    (item) => declarationFor(catalog, item.component)?.label ?? item.component,
  );
  return labels.length === 0 ? null : labels.join(' and ');
}

export function dialogSubtitle(node: GraphNode, catalog: Catalog): string {
  const host = declarationFor(catalog, node.component)?.label ?? node.component;
  const embedded = embeddedLabel(node, catalog);
  return embedded === null ? host : `${host} · with ${embedded}`;
}

/** Validate the document before and after the dialog's changes, through the API. */
async function check(
  props: NodeDialogProps,
  working: GraphDocument,
): Promise<{problems: Diagnostic[]; after: Diagnostic[]} | string> {
  try {
    const [before, after] = await Promise.all([
      props.client.validate(props.document),
      props.client.validate(working),
    ]);
    return {problems: introducedErrors(before, after, props.nodeId), after};
  } catch (error) {
    return `Could not check the changes: ${errorMessage(error)}`;
  }
}

/** Applies the working document once it introduces no error on the node. */
function useApply(props: NodeDialogProps, working: GraphDocument) {
  const [problems, setProblems] = useState<readonly Diagnostic[]>([]);
  const [failure, setFailure] = useState<string | null>(null);
  const apply = async (): Promise<void> => {
    const checked = await check(props, working);
    setFailure(typeof checked === 'string' ? checked : null);
    if (typeof checked === 'string') return;
    setProblems(checked.problems);
    if (checked.problems.length === 0) props.onApplied(working, checked.after);
  };
  return {problems, failure, apply};
}

export function useNodeDialog(props: NodeDialogProps): NodeDialogState {
  const [working, setWorking] = useState(props.document);
  const [tab, setTab] = useState(props.section);
  const [removing, setRemoving] = useState<EmbeddedPosition | null>(null);
  const {problems, failure, apply} = useApply(props, working);
  const remove = (): void => {
    if (removing === null) return;
    setWorking(removeEmbedded(working, props.nodeId, props.catalog, removing));
    setRemoving(null);
  };
  return {
    working,
    setWorking,
    tab,
    setTab,
    removing,
    setRemoving,
    problems,
    failure,
    apply,
    remove,
  };
}
