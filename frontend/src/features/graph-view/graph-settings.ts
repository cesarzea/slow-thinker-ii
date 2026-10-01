import {useState} from 'react';

export interface GraphSettings {
  readonly execution: boolean;
  readonly configuration: boolean;
  readonly system: boolean;
  readonly layout: number;
  readonly onMode: (value: boolean) => void;
  readonly onConfiguration: (value: boolean) => void;
  readonly onSystem: (value: boolean) => void;
  readonly onOrganize: () => void;
}
export function useGraphSettings(initialExecution: boolean): GraphSettings {
  const [execution, onMode] = useState(initialExecution);
  const [configuration, onConfiguration] = useState(false);
  const [system, onSystem] = useState(false);
  const [layout, organize] = useState(0);
  return {
    execution,
    configuration,
    system,
    layout,
    onMode,
    onConfiguration,
    onSystem,
    onOrganize: () => {
      organize((previous) => previous + 1);
    },
  };
}
