import {useEffect, useState} from 'react';
import {leavesEditor, parseRoute, routeHash} from './routes.ts';
import type {Route} from './routes.ts';

type Request = (action: () => void) => void;
export type Navigate = (route: Route, guarded?: boolean) => void;

function replaceHash(route: Route): void {
  if (routeHash(route) !== window.location.hash)
    window.history.replaceState(null, '', routeHash(route));
}

function currentRoute(): Route {
  const route = parseRoute(window.location.hash);
  replaceHash(route);
  return route;
}

function useHashChanges(route: Route, request: Request, show: (route: Route) => void): void {
  useEffect(() => {
    const changed = (): void => {
      const next = parseRoute(window.location.hash);
      if (!leavesEditor(route, next)) {
        replaceHash(next);
        show(next);
        return;
      }
      replaceHash(route);
      request(() => {
        window.history.pushState(null, '', routeHash(next));
        show(next);
      });
    };
    window.addEventListener('hashchange', changed);
    return () => {
      window.removeEventListener('hashchange', changed);
    };
  }, [route, request, show]);
}

/** Hash routing; leaving an editor goes through the unsaved-changes guard. */
export function useRoute(request: Request): {route: Route; navigate: Navigate} {
  const [route, setRoute] = useState<Route>(currentRoute);
  useHashChanges(route, request, setRoute);
  const move = (next: Route): void => {
    window.history.pushState(null, '', routeHash(next));
    setRoute(next);
  };
  const navigate: Navigate = (next, guarded = true) => {
    if (guarded && leavesEditor(route, next))
      request(() => {
        move(next);
      });
    else move(next);
  };
  return {route, navigate};
}
