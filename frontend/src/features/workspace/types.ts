import type {ConfigurationCatalog, PatchOperation} from '../../api/index.ts';
import type {SourceValue} from '../../ui/index.ts';

export interface SourceWorkspaceProps {
  readonly source: string;
  readonly locked: boolean;
  readonly catalog: ConfigurationCatalog | null;
  readonly patch: (operations: readonly PatchOperation[]) => Promise<void>;
}
export interface ComponentFormProps extends SourceWorkspaceProps {
  readonly id: string;
  readonly component: SourceValue;
}
