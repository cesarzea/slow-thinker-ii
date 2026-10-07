import {useId} from 'react';
import type {ReactElement} from 'react';
import {IconButton} from './button.tsx';

export interface SummaryEntry {
  readonly label: string;
  readonly value: string;
}
export interface ConfigurationSummaryProps {
  readonly title: string;
  readonly values: readonly SummaryEntry[];
  readonly onEdit: () => void;
  /** A short tag after the title, for example the embedded component's label. */
  readonly marker?: string;
  /** One line shown at the end of the row, for example the main value. */
  readonly preview?: string;
  readonly disabled?: boolean;
  /**
   * With `onToggle`, a click on the row shows or hides the values; hidden values stay in the
   * page for the row to control. Without it, the values are always shown.
   */
  readonly expanded?: boolean;
  readonly onToggle?: () => void;
}

function RowContent(props: ConfigurationSummaryProps & {readonly previewId: string}): ReactElement {
  return (
    <>
      <span className="section-row-title">{props.title}</span>
      {props.marker !== undefined && <span className="tag">{props.marker}</span>}
      {props.preview !== undefined && (
        <span id={props.previewId} className="section-row-preview">
          {props.preview}
        </span>
      )}
    </>
  );
}

function RowHead(props: ConfigurationSummaryProps & {readonly valuesId: string}): ReactElement {
  const previewId = useId();
  if (props.onToggle === undefined)
    return (
      <div className="section-row-toggle">
        <RowContent {...props} previewId={previewId} />
      </div>
    );
  return (
    <button
      type="button"
      className="section-row-toggle"
      aria-label={props.title}
      aria-describedby={props.preview === undefined ? undefined : previewId}
      aria-expanded={props.expanded === true}
      aria-controls={props.valuesId}
      onClick={props.onToggle}
    >
      <RowContent {...props} previewId={previewId} />
    </button>
  );
}

/** One configuration section as a row with Edit; its values show below it. */
export function ConfigurationSummary(props: ConfigurationSummaryProps): ReactElement {
  const values = useId();
  const collapsed = props.onToggle !== undefined && props.expanded !== true;
  return (
    <section className="section-row" aria-label={props.title}>
      <div className="section-row-head">
        <RowHead {...props} valuesId={values} />
        <IconButton
          icon="edit"
          size="sm"
          label={`Edit ${props.title}`}
          disabled={props.disabled === true}
          onClick={props.onEdit}
        />
      </div>
      <dl id={values} className="section-row-values" hidden={collapsed}>
        {props.values.map((entry, index) => (
          <div key={`${entry.label}:${String(index)}`}>
            <dt>{entry.label}</dt>
            <dd>{entry.value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
