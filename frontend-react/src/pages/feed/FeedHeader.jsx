import Badge from '../../components/atoms/Badge.jsx';
import { formatLongDate } from '../../lib/format.js';
import styles from './FeedHeader.module.css';

export default function FeedHeader({ batch, count }) {
  const nice = batch ? formatLongDate(batch.completed_at || batch.created_at) : '';
  const sub =
    batch && nice
      ? `${nice} · ${count} paper${count === 1 ? '' : 's'}`
      : `${count} paper${count === 1 ? '' : 's'}`;
  const pill = batch
    ? `Daily batch${batch.algorithm_version ? ` · ${batch.algorithm_version}` : ''}`
    : 'No completed batch';

  return (
    <div className={styles.header}>
      <div>
        <div className={styles.title}>Today's Feed</div>
        <div className={styles.sub}>{sub}</div>
      </div>
      <Badge variant="batch">{pill}</Badge>
    </div>
  );
}
