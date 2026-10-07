import {vi} from 'vitest';

class ResizeObserverStub {
  constructor(private readonly callback: ResizeObserverCallback) {}

  observe(target: Element): void {
    const element = target as HTMLElement;
    const contentRect = {width: element.offsetWidth, height: element.offsetHeight};
    const entry = {target, contentRect} as unknown as ResizeObserverEntry;
    this.callback([entry], this);
  }

  unobserve(): void {
    return;
  }

  disconnect(): void {
    return;
  }
}

class DOMMatrixReadOnlyStub {
  readonly m22: number;

  constructor(transform?: string) {
    const scale = /scale\(([\d.]+)\)/u.exec(transform ?? '')?.[1];
    this.m22 = scale === undefined ? 1 : Number(scale);
  }
}

function size(element: HTMLElement, dimension: 'width' | 'height', fallback: number): number {
  const value = Number.parseFloat(element.style[dimension]);
  return Number.isNaN(value) ? fallback : value;
}

/** jsdom has no layout: give React Flow observers, matrices and element sizes to measure. */
export function installFlowEnvironment(): void {
  vi.stubGlobal('ResizeObserver', ResizeObserverStub);
  vi.stubGlobal('DOMMatrixReadOnly', DOMMatrixReadOnlyStub);
  Object.defineProperties(HTMLElement.prototype, {
    offsetHeight: {
      configurable: true,
      get(this: HTMLElement) {
        return size(this, 'height', 120);
      },
    },
    offsetWidth: {
      configurable: true,
      get(this: HTMLElement) {
        return size(this, 'width', 220);
      },
    },
  });
  Object.defineProperty(Document.prototype, 'elementFromPoint', {
    configurable: true,
    value: () => null,
  });
  Object.defineProperty(SVGElement.prototype, 'getBBox', {
    configurable: true,
    value: () => ({x: 0, y: 0, width: 12, height: 12}),
  });
}
