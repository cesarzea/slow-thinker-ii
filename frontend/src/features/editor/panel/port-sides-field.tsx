import {useState} from 'react';
import type {ReactElement} from 'react';
import type {Catalog, GraphDocument, GraphNode} from '../../../api/index.ts';
import {ChoiceControl} from '../../../ui/index.ts';
import {nodeSides, PORT_SIDES, sidesMode, verticalSides, withSides} from '../state/port-sides.ts';
import type {PortSide, SidesMode} from '../state/port-sides.ts';
import {nodePorts} from '../state/ports.ts';

type Update = (document: GraphDocument) => GraphDocument;
interface Props {
  readonly document: GraphDocument;
  readonly node: GraphNode;
  readonly catalog: Catalog;
  readonly onChange: (update: Update) => void;
}

const MODES: readonly {value: SidesMode; label: string}[] = [
  {value: 'sides', label: 'Left and right'},
  {value: 'vertical', label: 'Top and bottom'},
  {value: 'custom', label: 'Custom'},
];
const SIDE_CHOICES = PORT_SIDES.map((side) => ({
  value: side,
  label: `${side.charAt(0).toUpperCase()}${side.slice(1)}`,
}));

/** "Input", "Output", or both when an input and an output share the name. */
function kindOf(port: string, inputs: readonly string[], outputs: readonly string[]): string {
  if (!inputs.includes(port)) return 'Output';
  return outputs.includes(port) ? 'Input and output' : 'Input';
}

/** One side select per port; an input and an output that share a name share their side. */
function CustomSides(props: Props): ReactElement {
  const {document, node, catalog} = props;
  const sides = nodeSides(document, node, catalog);
  const {inputs, outputs} = nodePorts(node, catalog);
  const choose = (port: string, value: string): void => {
    const side: PortSide = PORT_SIDES.find((item) => item === value) ?? 'left';
    props.onChange((current) =>
      withSides(current, node.id, {...nodeSides(current, node, catalog), [port]: side}),
    );
  };
  return (
    <div className="port-sides">
      {[...new Set([...inputs, ...outputs])].map((port) => (
        <ChoiceControl
          key={port}
          label={`${kindOf(port, inputs, outputs)} ${port}`}
          value={sides[port] ?? 'left'}
          choices={SIDE_CHOICES}
          onValue={(value) => {
            choose(port, value);
          }}
        />
      ))}
    </div>
  );
}

/** Where the node's ports sit: left and right, top and bottom, or a side chosen per port. */
export function PortSides(props: Props): ReactElement | null {
  const {document, node, catalog} = props;
  const [custom, setCustom] = useState(false);
  const {inputs, outputs} = nodePorts(node, catalog);
  if (inputs.length + outputs.length === 0) return null;
  const mode = custom ? 'custom' : sidesMode(document, node, catalog);
  const choose = (value: string): void => {
    setCustom(value === 'custom');
    if (value === 'sides') props.onChange((current) => withSides(current, node.id, null));
    if (value === 'vertical')
      props.onChange((current) => withSides(current, node.id, verticalSides(node, catalog)));
  };
  return (
    <section className="inspector-section" aria-label="Ports">
      <h3 className="panel-title">Ports</h3>
      <ChoiceControl label="Port sides" value={mode} choices={MODES} onValue={choose} />
      {mode === 'custom' && <CustomSides {...props} />}
    </section>
  );
}
