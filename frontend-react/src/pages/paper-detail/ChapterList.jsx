import styles from './ChapterList.module.css';

export default function ChapterList({ chapters }) {
  return (
    <div className={styles.list}>
      {chapters.map((ch) => (
        <button
          key={ch.time}
          type="button"
          className={[styles.chapter, ch.active ? styles.active : ''].join(' ').trim()}
        >
          <div className={styles.dot} />
          <div className={styles.time}>{ch.time}</div>
          <div className={styles.title}>{ch.label}</div>
        </button>
      ))}
    </div>
  );
}
