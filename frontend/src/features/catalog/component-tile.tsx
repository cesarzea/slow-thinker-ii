import type {ReactElement} from 'react';
import type {ComponentIcon} from '../../api/index.ts';

const GLYPHS: Readonly<Record<ComponentIcon, readonly string[]>> = {
  trigger: ['M21 12a9 9 0 1 1-18 0a9 9 0 1 1 18 0', 'm10 8 6 4-6 4z'],
  agent: [
    'M12 3l1.9 4.6 4.6 1.9-4.6 1.9L12 16l-1.9-4.6-4.6-1.9 4.6-1.9z',
    'M19 15l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z',
  ],
  memory: [
    'M4 5a8 3 0 1 0 16 0a8 3 0 1 0-16 0',
    'M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5',
    'M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3',
  ],
  router: ['M16 3h5v5', 'M8 3H3v5', 'M12 22v-8.3a4 4 0 0 0-1.2-2.9L3 3', 'm15 9 6-6'],
  output: [
    'M22 12h-6l-2 3h-4l-2-3H2',
    'M5.5 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.5-6.9A2 2 0 0 0 16.8 4H7.2a2 2 0 0 0-1.7 1.1z',
  ],
  component: ['M4 7l8-4 8 4v10l-8 4-8-4z', 'M4 7l8 4 8-4', 'M12 11v10'],
};

/** The component's coloured icon tile; decorative, the card names the component. */
export function ComponentTile({icon}: {readonly icon: ComponentIcon}): ReactElement {
  return (
    <span className={`catalog-tile tile-${icon}`} aria-hidden="true">
      <svg viewBox="0 0 24 24" focusable="false">
        {GLYPHS[icon].map((path) => (
          <path key={path} d={path} />
        ))}
      </svg>
    </span>
  );
}
