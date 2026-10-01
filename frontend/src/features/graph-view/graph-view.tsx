import type {ReactElement} from 'react';
import {GraphControls} from './graph-controls.tsx';
import {GraphList} from './graph-list.tsx';
import {GraphCanvas} from './graph-canvas.tsx';
import {Resources} from './resources.tsx';
import {graphStructure, structureModel} from './structure-model.ts';
import {useGraphSettings} from './graph-settings.ts';
import type {GraphSettings} from './graph-settings.ts';
import type {GraphViewProps} from './types.ts';
import './graph-view.css';

export function GraphView(props: GraphViewProps): ReactElement {
  const settings = useGraphSettings(props.execution !== undefined);
  return (
    <section
      aria-label="Experiment graph"
      className={settings.configuration ? 'agent-graph configuration-visible' : 'agent-graph'}
    >
      <GraphControls {...settings} />
      <GraphContent {...props} settings={settings} />
    </section>
  );
}
function GraphContent(props: GraphViewProps & {readonly settings: GraphSettings}): ReactElement {
  const {settings} = props;
  const structure = graphStructure(props);
  const visual = structureModel(props, settings);
  const definition = props.detail === undefined ? 'fallback' : 'definition';
  const identity = `${props.graph.graph_id}:${props.graph.revision}:${definition}:${String(settings.layout)}`;
  return (
    <>
      {props.detail === undefined && <p>Detailed structure unavailable. Showing catalog steps.</p>}
      {settings.execution && props.execution === undefined && (
        <p>No recorded activations available.</p>
      )}
      <GraphCanvas key={identity} {...visual} onSelect={props.onSelect} />
      <Resources structure={structure} onSelect={props.onSelect} />
      <GraphList structure={structure} execution={props.execution} onSelect={props.onSelect} />
    </>
  );
}
