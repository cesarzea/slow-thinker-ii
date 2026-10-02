import {useCallback, useEffect, useMemo, useRef, useState} from 'react';
import type {Dispatch, SetStateAction} from 'react';
import {ConfigurationClient, DefinitionError} from '../../api/index.ts';
import type {ConfigurationCatalog} from '../../api/index.ts';
import {acceptedLimits, commandBody, initialLimits} from './limits-model.ts';
import type {LimitName, LimitsState} from './limits-model.ts';

export interface LimitsModel {
  readonly state: LimitsState;
  readonly edit: (name: LimitName, value: string) => void;
  readonly submit: () => Promise<void>;
  readonly replay: () => Promise<void>;
  readonly useLatest: () => void;
}
export function useLimits(
  credential: string,
  catalog: ConfigurationCatalog,
  refresh: () => void,
): LimitsModel {
  const [state, update] = useState(() => initialLimits(catalog));
  const send = useLimitsSender(credential, update, refresh);
  return {
    state,
    ...localLimitsActions(state, catalog, update),
    submit: async () => {
      if (!state.pending && !state.uncertain) await send(commandBody(state));
    },
    replay: async () => {
      if (!state.pending && state.uncertain && state.frozen !== null) await send(state.frozen);
    },
  };
}
function useLimitsSender(
  credential: string,
  update: Dispatch<SetStateAction<LimitsState>>,
  refresh: () => void,
): (body: string) => Promise<void> {
  const active = useRef<AbortController | null>(null);
  const client = useMemo(() => new ConfigurationClient(credential), [credential]);
  useEffect(
    () => () => {
      active.current?.abort();
    },
    [],
  );
  const send = useCallback(
    async (body: string): Promise<void> => {
      if (active.current !== null) return;
      const controller = new AbortController();
      active.current = controller;
      update((previous) => ({...previous, frozen: body, pending: true, message: null}));
      await sendLimits(client, body, controller, update, refresh);
      if (active.current === controller) active.current = null;
    },
    [client, refresh, update],
  );
  return send;
}

function localLimitsActions(
  state: LimitsState,
  catalog: ConfigurationCatalog,
  update: Dispatch<SetStateAction<LimitsState>>,
): Pick<LimitsModel, 'edit' | 'useLatest'> {
  return {
    edit: (name, value) => {
      if (!state.pending && !state.uncertain)
        update({...state, edits: {...state.edits, [name]: value}, message: null});
    },
    useLatest: () => {
      if (!state.pending && !state.uncertain) update(initialLimits(catalog));
    },
  };
}

async function sendLimits(
  client: ConfigurationClient,
  body: string,
  controller: AbortController,
  update: Dispatch<SetStateAction<LimitsState>>,
  refresh: () => void,
): Promise<void> {
  try {
    const receipt = await client.limits(body, controller.signal);
    if (controller.signal.aborted) return;
    update((state) => acceptedLimits(state, body, receipt.configuration_revision));
    refresh();
  } catch (error) {
    if (controller.signal.aborted) return;
    const certain = error instanceof DefinitionError;
    update((state) => ({
      ...state,
      pending: false,
      uncertain: !certain,
      frozen: certain ? null : body,
      message: certain
        ? `${error.code}: ${error.message}`
        : 'Configuration update unconfirmed. Replay the unchanged command to recover.',
    }));
  }
}
