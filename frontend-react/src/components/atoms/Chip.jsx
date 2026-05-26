import styles from './Chip.module.css';

/**
 * Small pill — used in legend rows, frequency selectors, filter rows.
 * @param {Object} props
 * @param {React.ReactNode} props.children
 * @param {boolean} [props.selected]
 * @param {boolean} [props.outline]  rounded-20px variant used in reading-list filter bar
 * @param {() => void} [props.onClick]
 */
export default function Chip({ children, selected, outline, onClick }) {
  return (
    <button
      type="button"
      className={[
        styles.chip,
        outline ? styles.outline : '',
        selected ? styles.selected : '',
      ]
        .join(' ')
        .trim()}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
