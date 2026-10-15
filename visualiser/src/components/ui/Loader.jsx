
import { useEffect, useState } from "react";
import "./ui.css";
import Accordion from "./Accordion";

export default function Loader() {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const start = Date.now();
    const interval = setInterval(() => {
      setElapsed(Date.now() - start);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const isLongerWait = elapsed >= 8000;

  return (
    <div
      className="loader"
      role="status"
      aria-live="polite"
    >
        <div className="loader-header">
            <Accordion />
            <h2>Origami.io</h2>
        </div>
     

        <p className="loader-title">
            {isLongerWait
            ? "Starting simulation server..."
            : "Loading simulation..."}
        </p>

        <p className="loader-description">
            Hosted on Render`s free tier. The server may need a moment to restart after inactivity.
        </p>
    </div>
  );
}
