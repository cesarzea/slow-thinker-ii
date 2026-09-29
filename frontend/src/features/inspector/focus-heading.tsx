import {useEffect, useRef} from 'react';
import type {ReactElement, ReactNode} from 'react';

interface Props {
  readonly request: number | undefined;
  readonly children: ReactNode;
  readonly level?: 'h2' | 'h3';
}

export function FocusHeading({request, children, level: Heading = 'h3'}: Props): ReactElement {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    if (request === undefined) return;
    heading.current?.focus();
    return keepFocusedVisible(heading.current);
  }, [request]);
  return (
    <Heading ref={heading} tabIndex={-1}>
      {children}
    </Heading>
  );
}

function keepFocusedVisible(heading: HTMLHeadingElement | null): (() => void) | undefined {
  if (heading === null || typeof ResizeObserver === 'undefined') return undefined;
  const inspector = heading.closest('.inspector');
  if (inspector === null) return undefined;
  const observer = new ResizeObserver(() => {
    if (document.activeElement === heading) heading.scrollIntoView({block: 'nearest'});
  });
  observer.observe(inspector);
  return () => {
    observer.disconnect();
  };
}
