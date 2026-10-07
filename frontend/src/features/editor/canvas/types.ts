import type {Edge, Node} from '@xyflow/react';
import type {ComponentIcon} from '../../../api/index.ts';
import type {PortKind, PortSide} from '../state/port-sides.ts';

/** A value shown on a card: plain text, or a chip for an LLM. */
export interface CardValue {
  readonly text: string;
  readonly chip: boolean;
}
/** The embedded output component a card shows in its band. */
export interface CardBand {
  readonly label: string;
  readonly icon: ComponentIcon;
}
/** A port as its card draws it: on its side, with what it is connected to. */
export interface CardPort {
  readonly name: string;
  readonly kind: PortKind;
  readonly side: PortSide;
  /** An output of the embedded component shown in the card's band. */
  readonly band: boolean;
  /** "<node> · <port>" for each port it is connected to. */
  readonly links: readonly string[];
}
export interface CardData extends Record<string, unknown> {
  readonly name: string;
  readonly label: string;
  readonly icon: ComponentIcon;
  readonly values: readonly CardValue[];
  readonly inputs: readonly string[];
  readonly outputs: readonly string[];
  /** The inputs then the outputs, each on its side. */
  readonly ports: readonly CardPort[];
  readonly band: CardBand | null;
  /** The node's memory: its label and how many exchanges it keeps; null without one. */
  readonly memory: string | null;
  readonly problem: string | null;
  readonly activations: number | null;
  readonly interactive: boolean;
}
export type CardNode = Node<CardData, 'card'>;

interface RouteData extends Record<string, unknown> {
  /** Hovered or selected: drawn in the accent colour with its source port's name. */
  readonly active?: boolean;
  /** The connection's port references, and "<node> · <port> to <node> · <port>". */
  readonly from: string;
  readonly to: string;
  readonly route: string;
}
export type RouteEdgeType = Edge<RouteData, 'route'>;
