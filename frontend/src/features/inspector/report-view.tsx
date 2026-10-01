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
    <section aria-label="Component reports">
      <h4>Information reported by the component</h4>
      {reports.length === 0 ? (
        <p>Reasoning unavailable: the component supplied no reports.</p>
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
      {report.kind} · Reported · Schema {report.schema_version} · Event {report.event_sequence}
      {report.source_occurred_at !== null &&
        ` · Source timestamp: ${String(report.source_occurred_at)}`}
      <EvidenceLink identity={report.payload_id} select={onPayload}>
        View report
      </EvidenceLink>
      {report.payload_id === null && <p>Report content unavailable.</p>}
    </li>
  );
}
