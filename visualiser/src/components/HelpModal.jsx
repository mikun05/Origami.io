
import { useEffect } from 'react';
import '../HelpModal.css';

export default function HelpModal({ isOpen, onClose }) {
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') onClose();
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="help-backdrop" onClick={onClose}>
      <section
        className="help-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="help-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="help-header">
          <h2 id="help-title">How to use the simulator</h2>
          <button
            className="help-close"
            onClick={onClose}
            aria-label="Close instructions"
          >
            &times;
          </button>
        </header>

        <h3>Getting started</h3>
        <ol>
          <li><strong>Select a vertex.</strong> Click an interior vertex to fold from it. Outer vertices cannot be folded.</li>
          <li><strong>Choose an angle.</strong> Set your target angle, then click Fold or Animate.</li>
          <li><strong>Explore patterns.</strong> Select different crease patterns using the dropdown.</li>
        </ol>

        <p>
          The simulator aims for a uniform fold, bringing the
          mean fold angle as close as possible to your target.
        </p>

        <h3>Numerical settings</h3>
        <dl>
          <dt>Numerical Method</dt>
          <dd>Algorithm used to calculate the fold.</dd>
          <dt>Max Iterations</dt>
          <dd>Maximum number of optimisation steps.</dd>
          <dt>ftol</dt>
          <dd>Minimum improvement required before the solver stops.</dd>
          <dt>eps</dt>
          <dd>Step size used to estimate derivatives.</dd>
        </dl>

        <h3>Understanding the results</h3>
        <dl>
          <dt>Rotation Error</dt>
          <dd>How closely rotation constraints are satisfied. Lower is better.</dd>
          <dt>Mean of Angles</dt>
          <dd>Average fold angle achieved.</dd>
          <dt>Edge Changes</dt>
          <dd>How much the edges stretch or compress.</dd>
          <dt>Sector Angle Changes</dt>
          <dd>How much the angles between creases change.</dd>
        </dl>

        <p className="help-note">
          Ideally, the fold reaches your target angle while
          preserving the original geometry.
        </p>
      </section>
    </div>
  );
}
