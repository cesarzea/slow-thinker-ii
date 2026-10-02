export interface SourceValue {
  readonly raw: string;
  readonly entries: ReadonlyMap<string, SourceValue>;
  readonly items: readonly SourceValue[];
}

export function sourceTree(source: string): SourceValue | null {
  try {
    JSON.parse(source);
    return new SourceReader(source).value(0);
  } catch {
    return null;
  }
}

class SourceReader {
  private position = 0;
  constructor(private readonly source: string) {}

  value(depth: number): SourceValue {
    if (depth > 64) throw new Error('Source nesting exceeds the form preview bound.');
    this.space();
    const start = this.position;
    const entries = new Map<string, SourceValue>();
    const items: SourceValue[] = [];
    const token = this.source[this.position];
    if (token === '{') this.object(entries, depth);
    else if (token === '[') this.array(items, depth);
    else if (token === '"') this.string();
    else
      while (
        this.position < this.source.length &&
        !/[\s,\]}]/u.test(this.source[this.position] ?? '')
      )
        this.position++;
    return {raw: this.source.slice(start, this.position), entries, items};
  }

  private object(entries: Map<string, SourceValue>, depth: number): void {
    this.position++;
    this.space();
    while (this.source[this.position] !== '}') {
      const start = this.position;
      this.string();
      const key: unknown = JSON.parse(this.source.slice(start, this.position));
      if (typeof key !== 'string') throw new Error('Invalid object key.');
      this.space();
      this.position++;
      entries.set(key, this.value(depth + 1));
      this.space();
      if (this.source[this.position] !== ',') break;
      this.position++;
      this.space();
    }
    this.position++;
  }

  private array(items: SourceValue[], depth: number): void {
    this.position++;
    this.space();
    while (this.source[this.position] !== ']') {
      items.push(this.value(depth + 1));
      this.space();
      if (this.source[this.position] !== ',') break;
      this.position++;
    }
    this.position++;
  }

  private string(): void {
    this.position++;
    while (this.position < this.source.length) {
      const token = this.source[this.position++];
      if (token === '\\') this.position++;
      else if (token === '"') return;
    }
  }

  private space(): void {
    while (/\s/u.test(this.source[this.position] ?? 'x')) this.position++;
  }
}

export function pointerToken(value: string): string {
  return value.replaceAll('~', '~0').replaceAll('/', '~1');
}

export function sourceString(value: SourceValue | undefined): string {
  if (value === undefined) return '';
  try {
    const parsed: unknown = JSON.parse(value.raw);
    return typeof parsed === 'string' ? parsed : '';
  } catch {
    return '';
  }
}
