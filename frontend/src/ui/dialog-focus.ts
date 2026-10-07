import type {KeyboardEvent} from 'react';

const FOCUSABLE =
  'button:not(:disabled), input:not(:disabled):not([type="hidden"]), textarea:not(:disabled), select:not(:disabled), a[href], summary, [tabindex="0"]';

export function focusable(panel: HTMLElement | null): HTMLElement[] {
  return [...(panel?.querySelectorAll<HTMLElement>(FOCUSABLE) ?? [])].filter(visibleFocusTarget);
}

/** Close on Escape and keep Tab inside the dialog; handled keys do not reach outer dialogs. */
export function dialogKey(
  event: KeyboardEvent,
  panel: HTMLElement | null,
  close: () => void,
): void {
  if (event.key === 'Escape') {
    event.preventDefault();
    event.stopPropagation();
    close();
    return;
  }
  if (event.key !== 'Tab') return;
  event.stopPropagation();
  trapTab(event, panel);
}

function trapTab(event: KeyboardEvent, panel: HTMLElement | null): void {
  const targets = focusable(panel);
  const first = targets[0] ?? panel;
  const last = targets.at(-1) ?? panel;
  const edge = event.shiftKey ? first : last;
  if (
    !targets.some((target) => target === document.activeElement) ||
    document.activeElement === edge
  ) {
    event.preventDefault();
    const target = event.shiftKey ? last : first;
    target?.focus();
  }
}

function visibleFocusTarget(element: HTMLElement): boolean {
  if (element.closest('[hidden], [inert]') !== null) return false;
  if (element.tabIndex < 0 && element.tagName !== 'SUMMARY') return false;
  let ancestor: HTMLElement | null = element;
  while (ancestor !== null) {
    const style = window.getComputedStyle(ancestor);
    if (style.display === 'none' || style.visibility === 'hidden') return false;
    ancestor = ancestor.parentElement;
  }
  return visibleInDetails(element);
}

function visibleInDetails(element: HTMLElement): boolean {
  let details = element.closest('details:not([open])');
  while (details !== null) {
    const summary = details.querySelector(':scope > summary');
    if (summary?.contains(element) !== true) return false;
    details = details.parentElement?.closest('details:not([open])') ?? null;
  }
  return true;
}
