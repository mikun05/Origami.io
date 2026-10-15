import { useEffect, useState } from "react";
import "./ui.css";

const PANELS = 10;
const PANEL_WIDTH = 30;
const PANEL_HEIGHT = 20;

const FRAMES = [0, 0.1, 0.35, 0.65, 0.9, 1];
const SEQUENCE = [0, 1, 2, 3, 4, 5, 4, 3, 2, 1];

function getFaces(progress) {
  const projectedWidth = PANEL_WIDTH * (1 - progress * 0.75);
  const width = PANELS * projectedWidth;
  const startX = (250 - width) / 2;

  return Array.from({ length: PANELS }, (_, i) => {
    const x = startX + i * projectedWidth;
    const nextX = x + projectedWidth;

    const depth = progress * 4;
    const leftOffset = i % 2 === 0 ? -depth : depth;
    const rightOffset = -leftOffset;

    return (
      <polygon
        key={i}
        points={`
          ${x},${leftOffset}
          ${nextX},${rightOffset}
          ${nextX},${PANEL_HEIGHT + rightOffset}
          ${x},${PANEL_HEIGHT + leftOffset}
        `}
        fill={i % 2 === 0 ? "#5868a851" : "#5868a8e3"}
        stroke="#5868a8"
        strokeWidth="0.7"
      />
    );
  });
}

export default function Accordion() {
  const [frame, setFrame] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setFrame(previous => (previous + 1) % SEQUENCE.length);
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <svg
      className="accordion"
      viewBox="0 -4 250 28"
      aria-hidden="true"
    >
      {getFaces(FRAMES[SEQUENCE[frame]])}
    </svg>
  );
}
