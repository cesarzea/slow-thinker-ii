import type {UiField} from '../api/index.ts';

type FieldWidth = NonNullable<UiField['width']>;
export type NumberFormat = NonNullable<UiField['format']>;

/** The declaration's default widths; other controls take the row. */
const DEFAULT_WIDTHS: Readonly<Partial<Record<UiField['control'], FieldWidth>>> = {
  number: 'sm',
  choice: 'md',
  list: 'md',
  text: 'lg',
};

function fieldWidth(field: UiField): FieldWidth {
  return field.width ?? DEFAULT_WIDTHS[field.control] ?? 'full';
}

/** Class names carrying a field's control, width, alignment and label position. */
export function fieldClass(field: UiField): string {
  const align = field.align ?? (field.control === 'number' ? 'end' : 'start');
  const label = field.label_position ?? 'top';
  return `config-field field-${field.control} width-${fieldWidth(field)} align-${align} label-${label}`;
}

/** A unit after the number takes a space when it is a word, as in “50 tokens”. */
function withSuffix(text: string, suffix: string | undefined): string {
  if (suffix === undefined || suffix === '') return text;
  return /^\p{L}/u.test(suffix) ? `${text} ${suffix}` : `${text}${suffix}`;
}

/** A number as the declaration's `format` shows it: decimals, grouping, prefix and suffix. */
export function formatNumber(value: number, format: NumberFormat | undefined): string {
  const decimals = format?.decimals;
  const digits =
    decimals === undefined
      ? {}
      : {minimumFractionDigits: decimals, maximumFractionDigits: decimals};
  const text = new Intl.NumberFormat('en', {useGrouping: format?.grouping === true, ...digits});
  return withSuffix(`${format?.prefix ?? ''}${text.format(value)}`, format?.suffix);
}

/** “1 to 384,000”, “from 0” or “up to 2” for a number's bounds, or nothing. */
export function boundsText(
  minimum: number | undefined,
  maximum: number | undefined,
): string | undefined {
  const show = (value: number): string => formatNumber(value, {grouping: true});
  if (minimum !== undefined && maximum !== undefined) return `${show(minimum)} to ${show(maximum)}`;
  if (minimum !== undefined) return `From ${show(minimum)}`;
  return maximum === undefined ? undefined : `Up to ${show(maximum)}`;
}
