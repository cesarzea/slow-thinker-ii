import type {
  Activation,
  Branch,
  ChangeSummary,
  GraphDetail,
  OperatorClient,
} from '../../../api/index.ts';

/** What the open branch's working copy is compared with. */
type Baseline = {readonly version: number} | {readonly change: number} | null;

/** The graph's active version, and how far the open branch has moved from its own head. */
export interface VersionState {
  /** The graph's active version, on whichever branch it is. */
  readonly active: number | null;
  readonly activeBranch: string | null;
  /** The number the next activation will create. */
  readonly next: number;
  /** The open branch's latest version. */
  readonly head: number | null;
  /** The branch's latest version, else the version or change it started from. */
  readonly since: Baseline;
  /** Changes of the open branch after that baseline. */
  readonly pending: number;
}

export const NO_VERSIONS: VersionState = {
  active: null,
  activeBranch: null,
  next: 1,
  head: null,
  since: null,
  pending: 0,
};

/** Up to this many of the branch's latest changes are counted. */
const COUNTED_CHANGES = 100;

/** Where a branch without a version of its own started: a version, a change, or nothing. */
function origin(branch: Branch | undefined): Baseline {
  if (branch === undefined) return null;
  if (branch.from_version !== null) return {version: branch.from_version};
  return branch.from_change === null ? null : {change: branch.from_change};
}

/**
 * The baseline and the changes after it. A branch without a version of its own compares
 * with where it started; its first change holds that document, so it is not counted.
 */
function baseline(
  branch: Branch | undefined,
  detail: GraphDetail,
  mine: readonly ChangeSummary[],
): Pick<VersionState, 'since' | 'pending'> {
  const head = branch?.head_version ?? null;
  if (head !== null) {
    const change = detail.versions.find((item) => item.version === head)?.change ?? 0;
    return {since: {version: head}, pending: mine.filter((item) => item.change > change).length};
  }
  const since = origin(branch);
  return {since, pending: since === null ? mine.length : Math.max(0, mine.length - 1)};
}

export function versionState(
  detail: GraphDetail,
  name: string,
  changes: readonly ChangeSummary[],
): VersionState {
  const branch = detail.branches.find((item) => item.name === name);
  const active = detail.versions.find((item) => item.version === detail.active_version);
  return {
    active: detail.active_version,
    activeBranch: active?.branch ?? null,
    next: Math.max(0, ...detail.versions.map((item) => item.version)) + 1,
    head: branch?.head_version ?? null,
    ...baseline(
      branch,
      detail,
      changes.filter((item) => item.branch === name),
    ),
  };
}

/** Read the versions of a graph and count the branch's changes since its baseline. */
export async function readVersions(
  client: OperatorClient,
  graphId: string,
  branch: string,
  signal?: AbortSignal,
): Promise<VersionState> {
  const [detail, changes] = await Promise.all([
    client.graph(graphId, signal),
    client.changes(graphId, {branch, limit: COUNTED_CHANGES}, signal),
  ]);
  return versionState(detail, branch, changes);
}

/** A save that stored a new change adds one change after the baseline. */
export function afterSave(
  versions: VersionState,
  previous: number | null,
  change: number,
): VersionState {
  return previous !== null && change <= previous
    ? versions
    : {...versions, pending: versions.pending + 1};
}

/** The activated change becomes the branch's head and the graph's active version. */
export function afterActivation(versions: VersionState, activation: Activation): VersionState {
  const {version, branch} = activation;
  return {
    active: version,
    activeBranch: branch,
    next: Math.max(versions.next, version + 1),
    head: version,
    since: {version},
    pending: 0,
  };
}
