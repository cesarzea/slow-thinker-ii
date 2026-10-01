import {useEffect, useState} from 'react';
import type {ReactElement} from 'react';
import {OperatorClient} from '../../api/index.ts';
import type {Run} from '../../api/index.ts';

export function ResultPanel({
  credential,
  run,
}: {
  readonly credential: string;
  readonly run: Run | null;
}): ReactElement | null {
  if (run?.state !== 'completed') return null;
  return <ResultView key={run.run_id} credential={credential} id={run.run_id} />;
}

function ResultView({
  credential,
  id,
}: {
  readonly credential: string;
  readonly id: string;
}): ReactElement {
  const [text, setText] = useState('Loading result…');
  useEffect(() => {
    const controller = new AbortController();
    void new OperatorClient(credential).result(id, controller.signal).then(
      (result) => {
        if (!controller.signal.aborted) setText(result);
      },
      () => {
        if (!controller.signal.aborted) setText('Could not load the result.');
      },
    );
    return () => {
      controller.abort();
    };
  }, [credential, id]);
  return (
    <section aria-label="Final result">
      <h2>Final result</h2>
      <pre>{text}</pre>
    </section>
  );
}
