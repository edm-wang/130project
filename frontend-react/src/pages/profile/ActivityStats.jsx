import Widget from '../../components/widgets/Widget.jsx';
import styles from '../../components/widgets/Widget.module.css';

export default function ActivityStats({ stats }) {
  return (
    <Widget title="Activity">
      {stats.map((row) => (
        <div key={row.label} className={styles.statRow}>
          <span className={styles.statLabel}>{row.label}</span>
          <span className={styles.statVal}>{row.value}</span>
        </div>
      ))}
    </Widget>
  );
}
