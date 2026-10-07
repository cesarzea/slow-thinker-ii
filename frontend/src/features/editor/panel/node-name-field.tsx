import {useState} from 'react';
import type {ReactElement} from 'react';

interface Props {
  readonly name: string;
  readonly onRename: (name: string) => void;
}

/** The node name as an editable title; it is committed on Enter or when it loses focus. */
export function NodeNameField({name, onRename}: Props): ReactElement {
  const [text, setText] = useState(name);
  const commit = (): void => {
    const trimmed = text.trim();
    if (trimmed === '' || trimmed.length > 80) {
      setText(name);
      return;
    }
    if (trimmed !== name) onRename(trimmed);
  };
  return (
    <input
      className="inline-name"
      type="text"
      aria-label="Node name"
      title="Rename the node"
      value={text}
      onChange={(event) => {
        setText(event.target.value);
      }}
      onBlur={commit}
      onKeyDown={(event) => {
        if (event.key === 'Enter') commit();
        if (event.key === 'Escape') setText(name);
      }}
    />
  );
}
