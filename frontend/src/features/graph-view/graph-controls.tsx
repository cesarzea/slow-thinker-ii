import type {ReactElement} from 'react';
import type {GraphLayers} from './types.ts';

interface Props {
  readonly execution: boolean;
  readonly expanded: boolean;
  readonly layers: GraphLayers;
  readonly onMode: (execution: boolean) => void;
  readonly onExpand: (expanded: boolean) => void;
  readonly onLayers: (layers: GraphLayers) => void;
  readonly onOrganize: () => void;
}
const layerNames = {
  control: 'Control',
  permission: 'Permisos',
  binding: 'Recursos',
  observed: 'Llamadas observadas',
};
export function GraphControls(props: Props): ReactElement {
  return (
    <fieldset>
      <legend>Vista del grafo</legend>
      <ModeButtons {...props} />
      <label>
        <input
          type="checkbox"
          checked={props.expanded}
          onChange={(event) => {
            props.onExpand(event.target.checked);
          }}
        />{' '}
        Mostrar componentes internos
      </label>
      <div className="actions">{layerEntries(props)}</div>
    </fieldset>
  );
}
function layerEntries(props: Props): ReactElement[] {
  return (['control', 'permission', 'binding', 'observed'] as const).map((layer) => (
    <label key={layer}>
      <input
        type="checkbox"
        checked={props.layers[layer]}
        disabled={layer === 'observed' && !props.execution}
        onChange={(event) => {
          props.onLayers({...props.layers, [layer]: event.target.checked});
        }}
      />{' '}
      {layerNames[layer]}
    </label>
  ));
}

function ModeButtons(props: Props): ReactElement {
  return (
    <div className="actions">
      <button
        aria-pressed={!props.execution}
        onClick={() => {
          props.onMode(false);
        }}
      >
        Estructura
      </button>
      <button
        aria-pressed={props.execution}
        onClick={() => {
          props.onMode(true);
        }}
      >
        Ejecución
      </button>
      <button onClick={props.onOrganize}>Reorganizar grafo</button>
    </div>
  );
}
