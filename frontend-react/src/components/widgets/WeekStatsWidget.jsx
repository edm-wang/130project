import StatCell from '../atoms/StatCell.jsx';
import Widget from './Widget.jsx';
import styles from './Widget.module.css';

/**
 * @param {Object} props
 * @param {{ value: string|number, label: string }[]} props.stats  4 entries laid out 2x2
 * @param {string} [props.title]
 */
export default function WeekStatsWidget({ stats, title = 'This Week' }) {
  return (
    <Widget title={title}>
      <div className={styles.statGrid} style={{ marginBottom: 8 }}>
        {stats.slice(0, 2).map((s) => (
          <StatCell key={s.label} value={s.value} label={s.label} />
        ))}
      </div>
      <div className={styles.statGrid}>
        {stats.slice(2, 4).map((s) => (
          <StatCell key={s.label} value={s.value} label={s.label} />
        ))}
      </div>
    </Widget>
  );
}
