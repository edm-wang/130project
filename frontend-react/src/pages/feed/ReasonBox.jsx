import styles from './ReasonBox.module.css';

export default function ReasonBox({ children }) {
  return (
    <div className={styles.reason}>
      <span className={styles.label}>Why recommended: </span>
      {children}
    </div>
  );
}
