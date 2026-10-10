import './ui.css';

export default function InfoButton({
  onClick,
  label = 'More information'
}) {
  return (
    <button
      type="button"
      className="info-button"
      aria-label={label}
      title={label}
      onClick={onClick}
    >
      i
    </button>
  );
}
