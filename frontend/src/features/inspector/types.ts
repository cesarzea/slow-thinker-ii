export interface InspectionSource {
  readonly credential: string;
  readonly run: string;
}
export interface InspectionLinks {
  readonly onCall: (id: string) => void;
  readonly onPayload: (id: string) => void;
}
export interface Paging {
  readonly cursor: string | undefined;
  readonly onPage: (cursor: string | undefined) => void;
}

export type InspectionSelection =
  | Readonly<{kind: 'call'; id: string}>
  | Readonly<{kind: 'activation'; id: string}>
  | Readonly<{kind: 'payload'; id: string}>;
