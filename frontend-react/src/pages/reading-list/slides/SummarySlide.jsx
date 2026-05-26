import styles from './Slides.module.css';

const CELLS = [
  { num: 12, label: 'PAPERS TODAY' },
  { num: 5, label: 'ALIGNMENT' },
  { num: '94%', label: 'AVG MATCH' },
  { num: 3, label: 'SAVED' },
];

export default function SummarySlide({ active }) {
  return (
    <div
      className={[styles.slide, styles.s5, active ? styles.active : ''].join(' ').trim()}
    >
      <div className={styles.label}>TODAY'S FEED · SUMMARY</div>
      <div className={styles.pTitle} style={{ marginBottom: 14 }}>
        12 Papers Reviewed
      </div>
      <div className={styles.s5Grid}>
        {CELLS.map((c) => (
          <div key={c.label} className={styles.s5Cell}>
            <div className={styles.s5Num}>{c.num}</div>
            <div className={styles.s5Lbl}>{c.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
