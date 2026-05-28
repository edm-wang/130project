import styles from './StatCell.module.css';

/**
 * @param {Object} props
 * @param {string|number} props.value
 * @param {string} props.label
 */
export default function StatCell({ value, label }) {
  return (
    <div className={styles.cell}>
      <div className={styles.num}>{value}</div>
      <div className={styles.label}>{label}</div>
    </div>
  );
}
