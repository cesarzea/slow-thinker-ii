import type {ReactElement} from 'react';

/** Line icons on a 24px grid, drawn with the current text colour. */
const shapes = {
  play: <path d="M7 5v14l11-7z" fill="currentColor" stroke="none" />,
  history: (
    <>
      <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
      <path d="M3 3v5h5" />
      <path d="M12 7v5l3 2" />
    </>
  ),
  runs: <path d="M22 12h-4l-3 9L9 3l-3 9H2" />,
  undo: (
    <>
      <path d="M9 14 4 9l5-5" />
      <path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11" />
    </>
  ),
  redo: (
    <>
      <path d="m15 14 5-5-5-5" />
      <path d="M20 9H9.5a5.5 5.5 0 0 0 0 11H13" />
    </>
  ),
  arrange: (
    <>
      <rect x="3" y="4" width="6" height="6" rx="1.5" />
      <rect x="15" y="4" width="6" height="6" rx="1.5" />
      <rect x="15" y="14" width="6" height="6" rx="1.5" />
      <path d="M9 7h6M18 10v4" />
    </>
  ),
  'zoom-in': <path d="M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14Zm9 16-3.5-3.5M11 8v6M8 11h6" />,
  'zoom-out': <path d="M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14Zm9 16-3.5-3.5M8 11h6" />,
  fit: (
    <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" />
  ),
  outline: <path d="M9 6h12M9 12h12M9 18h12M4 6h.01M4 12h.01M4 18h.01" />,
  search: <path d="M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14Zm9 16-3.5-3.5" />,
  close: <path d="M18 6 6 18M6 6l12 12" />,
  plus: <path d="M12 5v14M5 12h14" />,
  trash: <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" />,
  more: <path d="M12 5h.01M12 12h.01M12 19h.01" strokeWidth="3" />,
  edit: (
    <>
      <path d="M17 3a2.8 2.8 0 0 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
      <path d="m15 5 4 4" />
    </>
  ),
  check: <path d="M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm-4 9 3 3 5-6" />,
  tick: <path d="m5 12 5 5 9-10" />,
  alert: <path d="M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm0 5v5m0 3h.01" />,
  arrow: <path d="M5 12h14m-5-5 5 5-5 5" />,
  'chevron-down': <path d="m6 9 6 6 6-6" />,
  connection: <path d="M3 17h2c7 0 7-10 14-10h2M3 15v4M21 5v4" />,
  branch: (
    <path d="M6 3v12m0 0a3 3 0 1 0 0 6 3 3 0 0 0 0-6Zm12-9a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm0 0a9 9 0 0 1-9 9" />
  ),
  graph: (
    <path d="M6 3.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Zm12 0a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5ZM12 15.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5ZM8.5 6h7M7.2 8.2l3.6 7.6m6-7.6-3.6 7.6" />
  ),
  trigger: <path d="M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm-2 5 6 4-6 4z" />,
  llm: (
    <>
      <path d="m12 3 1.9 4.6 4.6 1.9-4.6 1.9L12 16l-1.9-4.6-4.6-1.9 4.6-1.9z" />
      <path d="m19 15 .8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z" />
    </>
  ),
  router: <path d="M16 3h5v5M8 3H3v5m9 14v-8.3a4 4 0 0 0-1.2-2.9L3 3m12 6 6-6" />,
  output: (
    <>
      <path d="M22 12h-6l-2 3h-4l-2-3H2" />
      <path d="M5.5 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.5-6.9A2 2 0 0 0 16.8 4H7.2a2 2 0 0 0-1.7 1.1z" />
    </>
  ),
  component: <path d="M21 8 12 3 3 8v8l9 5 9-5zM3 8l9 5 9-5m-9 5v8" />,
  memory: (
    <>
      <ellipse cx="12" cy="5" rx="8" ry="3" />
      <path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3" />
    </>
  ),
} as const;

export type IconName = keyof typeof shapes;

/** A decorative icon; the control that shows it carries the name. */
export function Icon({
  name,
  size = 16,
}: {
  readonly name: IconName;
  readonly size?: number;
}): ReactElement {
  return (
    <svg
      className="icon"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {shapes[name]}
    </svg>
  );
}
