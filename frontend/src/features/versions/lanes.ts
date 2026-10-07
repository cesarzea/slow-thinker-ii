import type {Branch, VersionSummary} from '../../api/index.ts';

/** One version row of the branch graph, with the lines that cross or meet it. */
export interface LaneRow {
  readonly version: VersionSummary;
  readonly lane: number;
  /** A line leaves the dot downwards, towards the version this one follows. */
  readonly down: boolean;
  /** Lanes whose lines cross the row. */
  readonly through: readonly number[];
  /** Lanes whose lines come from above and end at the dot: its later versions. */
  readonly into: readonly number[];
}

export interface LaneGraph {
  /** Branch names, one lane each, oldest branch first. */
  readonly lanes: readonly string[];
  /** Versions, newest first. */
  readonly rows: readonly LaneRow[];
}

interface Edge {
  readonly child: number;
  readonly parent: number;
  readonly lane: number;
}

function laneNames(versions: readonly VersionSummary[], branches: readonly Branch[]): string[] {
  const used = new Set(versions.map((version) => version.branch));
  const known = branches.map((branch) => branch.name).filter((name) => used.has(name));
  const unknown = [...used]
    .filter((name) => !known.includes(name))
    .toSorted((a, b) => a.localeCompare(b, 'en'));
  return [...known, ...unknown];
}

function distinct(lanes: readonly number[]): number[] {
  return [...new Set(lanes)].toSorted((a, b) => a - b);
}

/**
 * Lays versions out git-graph style: one lane per branch that has versions, a row per
 * version, newest first, and a line from each version to the one it follows (`parent`),
 * which forks from another lane for a branch's first version.
 */
export function laneGraph(
  versions: readonly VersionSummary[],
  branches: readonly Branch[],
): LaneGraph {
  const lanes = laneNames(versions, branches);
  const ordered = versions.toSorted((a, b) => b.version - a.version);
  const rowOf = new Map(ordered.map((version, index) => [version.version, index]));
  const edges: Edge[] = ordered.flatMap((version, child) => {
    const parent = version.parent === null ? undefined : rowOf.get(version.parent);
    return parent === undefined ? [] : [{child, parent, lane: lanes.indexOf(version.branch)}];
  });
  const rows = ordered.map((version, index) => ({
    version,
    lane: lanes.indexOf(version.branch),
    down: edges.some((edge) => edge.child === index),
    through: distinct(
      edges.filter((edge) => edge.child < index && index < edge.parent).map((edge) => edge.lane),
    ),
    into: distinct(edges.filter((edge) => edge.parent === index).map((edge) => edge.lane)),
  }));
  return {lanes, rows};
}
