import type {ReactElement} from 'react';
import type {ReportView as Report} from '../../api/index.ts';
import {EvidenceLink} from './evidence-link.tsx';

export function ReportView({
  reports,
  onPayload,
}: {
  readonly reports: readonly Report[];
  readonly onPayload: (id: string) => void;
}): ReactElement {
  return (
    <section aria-label="Informes del componente">
      <h4>Información declarada por el componente</h4>
      {reports.length === 0 ? (
        <p>Razonamiento no disponible: el componente no aportó informes.</p>
      ) : (
        <ul>
          {reports.map((report) => (
            <ReportItem key={report.event_sequence} report={report} onPayload={onPayload} />
          ))}
        </ul>
      )}
    </section>
  );
}
function ReportItem({
  report,
  onPayload,
}: {
  readonly report: Report;
  readonly onPayload: (id: string) => void;
}): ReactElement {
  return (
    <li>
      {report.kind} · Declarado (reported) · Esquema {report.schema_version} · Evento{' '}
      {report.event_sequence}
      {report.source_occurred_at !== null &&
        ` · Marca temporal de origen: ${String(report.source_occurred_at)}`}
      <EvidenceLink identity={report.payload_id} select={onPayload}>
        Abrir informe
      </EvidenceLink>
      {report.payload_id === null && <p>Contenido del informe no disponible.</p>}
    </li>
  );
}
