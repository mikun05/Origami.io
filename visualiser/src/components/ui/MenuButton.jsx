import './ui.css';

export default function MenuButton({ onClick }) {
  return (
    <button
      type="button"
      className="menu-button"
      aria-label="Open help menu"
      onClick={onClick}
    >
      <span />
      <span />
      <span />
    </button>
  );
}