import { formatClock } from '../../lib/format.js';
import styles from './DigestChapterList.module.css';

export default function DigestChapterList({ chapters, activeIndex, onJump }) {
  return (
    <div className={styles.list}>
      {chapters.map((ch, i) => (
        <button
          key={i}
          type="button"
          className={[styles.item, i === activeIndex ? styles.active : ''].join(' ').trim()}
          onClick={() => onJump(i)}
        >
          <div className={styles.dot} />
          <div className={styles.time}>{formatClock(ch.start)}</div>
          <div className={styles.info}>
            <div className={styles.title}>{ch.label}</div>
            <div className={styles.sub}>{ch.sub}</div>
          </div>
        </button>
      ))}
    </div>
  );
}
