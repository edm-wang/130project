import styles from './Slides.module.css';

const VARIANT_TO_BG = {
  0: styles.s1,
  1: styles.s2,
  2: styles.s3,
};

/**
 * Shared header for the per-paper slides (label + title + authors).
 * The visualization body is rendered via children so callers can swap
 * between an insight box, a bar chart, or a stat strip.
 */
export default function PaperSlide({
  active,
  variantIndex = 0,
  label,
  title,
  authors,
  children,
}) {
  const bg = VARIANT_TO_BG[variantIndex] ?? styles.s1;
  return (
    <div className={[styles.slide, bg, active ? styles.active : ''].join(' ').trim()}>
      <div className={styles.label}>{label}</div>
      <div className={styles.pTitle}>{title}</div>
      <div className={styles.authors}>{authors}</div>
      {children}
    </div>
  );
}

export function InsightBody({ text }) {
  return <div className={styles.insight}>{text}</div>;
}

export function BarChartBody({ bars, caption }) {
  return (
    <div style={{ marginTop: 10 }}>
      <div className={styles.barChart}>
        {bars.map((bar) => (
          <div key={bar.label} className={styles.barWrap}>
            <div className={styles.barVal}>{bar.value}%</div>
            <div
              className={styles.bar}
              style={{ height: `${bar.value}px`, background: bar.color }}
            />
            <div className={styles.barLbl}>{bar.label}</div>
          </div>
        ))}
      </div>
      {caption ? <div className={styles.caption}>{caption}</div> : null}
    </div>
  );
}

export function StatStripBody({ stats }) {
  return (
    <div style={{ marginTop: 14, display: 'flex', gap: 22 }}>
      {stats.map((s) => (
        <div key={s.label} style={{ textAlign: 'center' }}>
          <div className={styles.bigStat}>{s.num}</div>
          <div className={styles.statDesc}>{s.label}</div>
        </div>
      ))}
    </div>
  );
}
