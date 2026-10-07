import type {GraphDocument, Limits} from '../../../api/index.ts';

/** Limits of a graph created in the editor. */
const DEFAULT_LIMITS: Limits = {
  max_activations: 20,
  max_running_nodes: 4,
  time_limit_seconds: 300,
  budget_usd: '0.10',
};

/** A local graph document with default limits and no nodes; it is stored at the first save. */
export function newGraphDocument(id: string, name: string): GraphDocument {
  return {
    format: 'slow-thinker.graph/1',
    id,
    name,
    limits: {...DEFAULT_LIMITS},
    nodes: [],
    connections: [],
    layout: {},
  };
}

const COLUMNS = 4;
const STEP_X = 270;
const STEP_Y = 240;
/**
 * Canvas cards are 220px wide. The tallest step 1 card, an LLM Call with an embedded Router
 * carrying two outputs, is 199px tall; each further port adds a row of about 18px.
 */
const CARD_WIDTH = 220;
const CARD_HEIGHT = 200;
/** The smallest space kept between a new card and any other card. */
const CARD_GAP = 24;

function clear([x, y]: readonly [number, number], [left, top]: readonly [number, number]): boolean {
  return Math.abs(left - x) >= CARD_WIDTH + CARD_GAP || Math.abs(top - y) >= CARD_HEIGHT + CARD_GAP;
}

/** The first grid position that keeps at least CARD_GAP between its card and every other card. */
export function freePosition(document: GraphDocument): [number, number] {
  const taken = Object.values(document.layout ?? {});
  for (let index = 0; index < 1000; index += 1) {
    const candidate: [number, number] = [
      40 + (index % COLUMNS) * STEP_X,
      40 + Math.floor(index / COLUMNS) * STEP_Y,
    ];
    if (taken.every((position) => clear(candidate, position))) return candidate;
  }
  return [40, Math.max(...taken.map(([, top]) => top)) + STEP_Y];
}
