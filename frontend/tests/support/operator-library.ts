import {reply} from './operator-data.ts';
import {singleDetail, summary} from './projection-data.ts';

/** Bundled reads for existing operator tests; authoring tests provide their own write fixture. */
export function operatorLibraryRead(
  path: string,
  detail: unknown,
  status: number,
): Response | null {
  if (path === '/definitions')
    return reply({
      items: [{...summary(singleDetail), origin: 'bundled', derived_from: null}],
      next_cursor: null,
    });
  if (path === '/definitions/detail') return reply(detail, status);
  if (path === '/definitions/source') return reply(singleDetail.definition, status);
  return null;
}
