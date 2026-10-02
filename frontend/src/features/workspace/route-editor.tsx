import {useState} from 'react';
import type {ReactElement} from 'react';
import {JsonField, TextControl, pointerToken} from '../../ui/index.ts';
import type {SourceValue} from '../../ui/index.ts';
import type {PatchOperation} from '../../api/index.ts';
import {controllerSource} from './source-config.ts';
import type {SourceWorkspaceProps} from './types.ts';
export function RouteEditor(props: SourceWorkspaceProps & {readonly path: string}): ReactElement {
  const [node, setNode] = useState('');
  const [port, setPort] = useState('');
  const [target, setTarget] = useState('');
  const routes = controllerSource(props.source).config?.entries.get('routes');
  const apply = (): void => {
    void props.patch(routePatch(props.path, routes, node, port, target));
  };
  return (
    <>
      <TextControl label="Route source node" value={node} onValue={setNode} />
      <TextControl label="Selected output port" value={port} onValue={setPort} />
      <TextControl label="Target node (empty exits)" value={target} onValue={setTarget} />
      <button disabled={props.locked || !node || !port} onClick={apply}>
        Apply conditional route
      </button>
      <JsonField
        label="Conditional routes"
        path={`${props.path}/routes`}
        raw={routes?.raw}
        disabled={props.locked}
        patch={props.patch}
      />
    </>
  );
}
function routePatch(
  path: string,
  routes: SourceValue | undefined,
  node: string,
  port: string,
  target: string,
): PatchOperation[] {
  const operations: PatchOperation[] = [];
  if (routes === undefined) operations.push({op: 'add', path: `${path}/routes`, value_json: '{}'});
  if (routes?.entries.has(node) !== true)
    operations.push({op: 'add', path: `${path}/routes/${pointerToken(node)}`, value_json: '{}'});
  operations.push({
    op: 'add',
    path: `${path}/routes/${pointerToken(node)}/${pointerToken(port)}`,
    value_json: target === '' ? 'null' : JSON.stringify(target),
  });
  return operations;
}
