import type {ReactElement} from 'react';
import type {Diagnostic, GraphNode} from '../../../api/index.ts';
import {Button, ConfigurationDialog, KindTile, Tabs} from '../../../ui/index.ts';
import type {TabGroup} from '../../../ui/index.ts';
import {RemoveComponentDialog} from '../panel/component-dialogs.tsx';
import {providedConnections} from '../state/embedding.ts';
import {declarationFor} from '../state/ports.ts';
import {dialogSubtitle, problemKey, useNodeDialog} from './node-dialog-state.ts';
import type {NodeDialogProps, NodeDialogState} from './node-dialog-state.ts';
import {SectionFields} from './section-fields.tsx';
import {keptSides} from '../state/port-sides.ts';
import {nodeSections, withSectionConfig} from './sections.ts';
import type {NodeSection} from './sections.ts';

type PartProps = NodeDialogProps & {readonly node: GraphNode; readonly dialog: NodeDialogState};

/** A group heading per component: its tile and label; embedded ones look the same. */
function groupOf(entry: NodeSection): TabGroup {
  const {declaration} = entry;
  return {label: declaration.label, icon: <KindTile icon={declaration.icon} size="sm" />};
}

function SectionPanel(props: PartProps & {readonly entry: NodeSection}): ReactElement {
  const {node, catalog, dialog, entry} = props;
  return (
    <>
      <h3 className="section-title">{entry.section.title}</h3>
      <SectionFields
        entry={entry}
        node={node}
        catalog={catalog}
        onConfig={(config) => {
          const next = withSectionConfig(dialog.working, node.id, entry, config);
          dialog.setWorking(keptSides(next, node.id, catalog));
        }}
      />
    </>
  );
}

function SectionTabs(props: PartProps & {readonly sections: readonly NodeSection[]}): ReactElement {
  const {dialog, sections} = props;
  const current = sections.find((entry) => entry.key === dialog.tab) ?? sections[0];
  const items = sections.map((entry) => ({
    key: entry.key,
    title: entry.section.title,
    group: groupOf(entry),
  }));
  return (
    <Tabs
      label="Sections"
      orientation="vertical"
      items={items}
      selected={current?.key ?? ''}
      onSelect={dialog.setTab}
    >
      {current !== undefined && <SectionPanel {...props} entry={current} />}
    </Tabs>
  );
}

/** The section the dialog shows: the selected tab, else the first. */
function currentEntry(props: PartProps): NodeSection | undefined {
  const sections = nodeSections(props.node, props.catalog);
  return sections.find((entry) => entry.key === props.dialog.tab) ?? sections[0];
}

/** Remove the embedded component whose section is shown; in the footer while one is. */
function RemoveAction(props: PartProps): ReactElement | null {
  const entry = currentEntry(props);
  if (entry?.position === undefined || entry.position === null) return null;
  const {position} = entry;
  return (
    <Button
      variant="danger"
      onClick={() => {
        props.dialog.setRemoving(position);
      }}
    >
      Remove {entry.declaration.label}
    </Button>
  );
}

function RemoveConfirmation({node, catalog, dialog}: PartProps): ReactElement | null {
  const {removing} = dialog;
  if (removing === null) return null;
  const embedded = (node.embedded ?? []).find((item) => item.position === removing);
  if (embedded === undefined) return null;
  const label = declarationFor(catalog, embedded.component)?.label ?? embedded.component;
  const connections =
    removing === 'output' ? providedConnections(dialog.working, node.id, catalog) : [];
  return (
    <RemoveComponentDialog
      label={label}
      document={dialog.working}
      connections={connections}
      onConfirm={dialog.remove}
      onCancel={() => {
        dialog.setRemoving(null);
      }}
    />
  );
}

function DialogProblems({problems}: {readonly problems: readonly Diagnostic[]}): ReactElement {
  return (
    <div role="alert" className="dialog-problems">
      <p>Fix these problems before applying, or cancel:</p>
      <ul>
        {problems.map((item) => (
          <li key={problemKey(item)}>{item.message}</li>
        ))}
      </ul>
    </div>
  );
}

/**
 * One dialog per node, of a fixed size and place: the section list on the left, the selected
 * section on the right, and Remove, Cancel and Apply in the footer.
 */
export function NodeDialog(props: NodeDialogProps): ReactElement | null {
  const dialog = useNodeDialog(props);
  const node = dialog.working.nodes.find((item) => item.id === props.nodeId);
  if (node === undefined) return null;
  const parts = {...props, node, dialog};
  return (
    <ConfigurationDialog
      title={node.name}
      subtitle={dialogSubtitle(node, props.catalog)}
      icon={<KindTile icon={declarationFor(props.catalog, node.component)?.icon ?? 'component'} />}
      note="Changes are saved when you apply them"
      fixed
      actions={<RemoveAction {...parts} />}
      error={dialog.failure}
      onApply={dialog.apply}
      onCancel={props.onCancel}
    >
      <SectionTabs {...parts} sections={nodeSections(node, props.catalog)} />
      {dialog.problems.length > 0 && <DialogProblems problems={dialog.problems} />}
      <RemoveConfirmation {...parts} />
    </ConfigurationDialog>
  );
}
