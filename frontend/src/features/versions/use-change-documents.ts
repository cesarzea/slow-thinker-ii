import {useEffect, useState} from 'react';
import type {ChangeRecord, GraphDocument, OperatorClient} from '../../api/index.ts';

type Documents = ReadonlyMap<number, GraphDocument>;

function missingChanges(wanted: string, documents: Documents): number[] {
  return wanted
    .split(',')
    .filter((part) => part !== '')
    .map(Number)
    .filter((change) => !documents.has(change));
}

function fulfilled(results: readonly PromiseSettledResult<ChangeRecord>[]): ChangeRecord[] {
  return results.flatMap((result) => (result.status === 'fulfilled' ? [result.value] : []));
}

/**
 * The documents of these changes, each read once since changes never change. A change
 * that cannot be read is left out, and its description falls back to its number.
 */
export function useChangeDocuments(
  client: OperatorClient,
  graphId: string,
  changes: readonly number[],
): Documents {
  const [documents, setDocuments] = useState<Documents>(new Map());
  const wanted = changes.join(',');
  useEffect(() => {
    const missing = missingChanges(wanted, documents);
    if (missing.length === 0) return;
    const controller = new AbortController();
    const reads = missing.map(async (change) => client.change(graphId, change, controller.signal));
    void Promise.allSettled(reads).then((results) => {
      const read = fulfilled(results);
      if (controller.signal.aborted || read.length === 0) return;
      setDocuments((now) => {
        const next = new Map(now);
        for (const record of read) next.set(record.change, record.document);
        return next;
      });
    });
    return () => {
      controller.abort();
    };
  }, [client, graphId, wanted, documents]);
  return documents;
}
