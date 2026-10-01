import type {ReactElement} from 'react';
import {Handle, Position} from '@xyflow/react';
import type {NodeProps} from '@xyflow/react';
import type {AgentConfiguration, AgentPresentation, VisualNode} from './types.ts';

export function AgentCard({data}: NodeProps<VisualNode>): ReactElement | null {
  const agent = data.agent;
  if (agent === undefined) return null;
  return (
    <article className="agent-card">
      <AgentHeading agent={agent} />
      {agent.activity !== undefined && (
        <p className="agent-activity">{activityLabel(agent.activity)}</p>
      )}
      {agent.configuration !== undefined && <Configuration configuration={agent.configuration} />}
      <AgentHandles />
    </article>
  );
}
function activityLabel(activity: NonNullable<AgentPresentation['activity']>): string {
  if (activity.count === 0) return 'No recorded activations';
  const noun = activity.count === 1 ? 'activation' : 'activations';
  return `${activity.state} · ${String(activity.count)} recorded ${noun}`;
}
function AgentHeading({agent}: {readonly agent: AgentPresentation}): ReactElement {
  return (
    <div className="agent-heading">
      <span
        className="agent-icon"
        role="img"
        aria-label={agent.knownAgent ? 'AI agent' : 'Component'}
      >
        {agent.knownAgent ? 'AI' : '◇'}
      </span>
      <div>
        <span className="agent-type">{agent.componentType}</span>
        <strong>{agent.name}</strong>
      </div>
    </div>
  );
}
function Configuration({
  configuration,
}: {
  readonly configuration: AgentConfiguration;
}): ReactElement {
  return (
    <dl className="agent-configuration">
      <div>
        <dt>Model</dt>
        <dd>
          {configuration.model.value}
          <small>{configuration.model.source}</small>
        </dd>
      </div>
      <div>
        <dt>Reasoning effort</dt>
        <dd>
          {configuration.effort.value}
          <small>{configuration.effort.source}</small>
        </dd>
      </div>
    </dl>
  );
}
function AgentHandles(): ReactElement {
  return (
    <>
      <Handle type="target" position={Position.Left} id="in" className="agent-connector" />
      <Handle type="source" position={Position.Right} id="out" className="agent-connector" />
      <Handle type="source" position={Position.Bottom} id="return-source" style={{left: '65%'}} />
      <Handle type="target" position={Position.Bottom} id="return-target" style={{left: '35%'}} />
    </>
  );
}
export function TerminalAnchor(): ReactElement {
  return (
    <span className="terminal-anchor" aria-hidden="true">
      <Handle type="target" position={Position.Left} id="in" />
    </span>
  );
}
export function EntryAnchor(): ReactElement {
  return (
    <span className="terminal-anchor" aria-hidden="true">
      <Handle type="source" position={Position.Right} id="out" />
    </span>
  );
}
