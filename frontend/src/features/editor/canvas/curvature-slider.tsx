import {useId, useState} from 'react';
import type {ReactElement} from 'react';
import type {CanvasModel} from './canvas-model.ts';
import {viewOf, withView} from './connection-style.ts';

export interface ViewProps {
  readonly model: CanvasModel;
  /** Shows a curvature on the canvas while the slider moves, or none once it is saved. */
  readonly onPreview: (curvature: number | null) => void;
}
type Props = ViewProps;

/** A curvature shown while the slider moves, and saved as one change once released. */
function useMovingCurvature(props: Props): {
  readonly moving: number | null;
  readonly move: (value: number) => void;
  readonly save: () => void;
} {
  const [moving, setMoving] = useState<number | null>(null);
  const move = (value: number): void => {
    setMoving(value);
    props.onPreview(value);
  };
  const save = (): void => {
    if (moving === null) return;
    const curvature = moving;
    props.model.change((value) => withView(value, {curvature}));
    setMoving(null);
    props.onPreview(null);
  };
  return {moving, move, save};
}

/** The curvature of curved connections: previewed while it moves, saved once on release. */
export function Curvature(props: Props): ReactElement {
  const id = useId();
  const saved = viewOf(props.model.document).curvature;
  const {moving, move, save} = useMovingCurvature(props);
  return (
    <div className="curvature">
      <label htmlFor={id}>Curvature</label>
      <input
        id={id}
        type="range"
        min={0}
        max={1}
        step={0.05}
        value={moving ?? saved}
        onChange={(event) => {
          move(Number(event.target.value));
        }}
        onPointerUp={save}
        onKeyUp={save}
        onBlur={save}
      />
      <output htmlFor={id}>{(moving ?? saved).toFixed(2)}</output>
    </div>
  );
}
