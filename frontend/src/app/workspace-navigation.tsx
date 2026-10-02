import type {ReactElement} from 'react';
export type WorkspacePage = 'Experiments' | 'Components' | 'Resources' | 'Runs' | 'Settings';
const pages: readonly WorkspacePage[] = [
  'Experiments',
  'Components',
  'Resources',
  'Runs',
  'Settings',
];
export function WorkspaceNavigation({
  page,
  select,
}: {
  readonly page: WorkspacePage;
  readonly select: (page: WorkspacePage) => void;
}): ReactElement {
  return (
    <nav aria-label="Workspace">
      <p className="nav-caption">Workspace</p>
      {pages.map((item) => (
        <button
          key={item}
          aria-current={page === item ? 'page' : undefined}
          onClick={() => {
            select(item);
          }}
        >
          {item}
        </button>
      ))}
    </nav>
  );
}
