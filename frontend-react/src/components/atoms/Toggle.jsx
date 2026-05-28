import styles from './Toggle.module.css';

/**
 * @param {Object} props
 * @param {boolean} props.on
 * @param {(next: boolean) => void} [props.onChange]
 * @param {string} [props.ariaLabel]
 */
export default function Toggle({ on, onChange, ariaLabel }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={on}
      aria-label={ariaLabel}
      className={[styles.toggle, on ? styles.on : styles.off].join(' ')}
      onClick={() => onChange && onChange(!on)}
    />
  );
}
