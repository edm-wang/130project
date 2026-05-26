import styles from './Slides.module.css';

const CLUSTERS = [
  {
    label: 'Alignment & RLHF',
    count: '5 papers',
    bg: 'rgba(29,158,117,0.08)',
    border: 'rgba(29,158,117,0.2)',
    color: '#9FE1CB',
  },
  {
    label: 'Generative Models',
    count: '3 papers',
    bg: 'rgba(143,119,221,0.08)',
    border: 'rgba(143,119,221,0.2)',
    color: '#AFA9EC',
  },
  {
    label: 'Efficiency & Scaling',
    count: '4 papers',
    bg: 'rgba(239,159,39,0.08)',
    border: 'rgba(239,159,39,0.2)',
    color: '#FAC775',
  },
];

export default function ThemeClustersSlide({ active }) {
  return (
    <div
      className={[styles.slide, styles.s4, active ? styles.active : ''].join(' ').trim()}
    >
      <div className={styles.label}>PAPERS 4 – 12 · THEME CLUSTERS</div>
      <div className={styles.pTitle} style={{ marginBottom: 14 }}>
        Key Themes Across{'\n'}Remaining Papers
      </div>
      <div style={{ width: '100%', maxWidth: 320 }}>
        {CLUSTERS.map((c) => (
          <div
            key={c.label}
            className={styles.clusterRow}
            style={{
              background: c.bg,
              border: `0.5px solid ${c.border}`,
              marginBottom: 6,
            }}
          >
            <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.7)' }}>
              {c.label}
            </span>
            <span
              style={{
                fontSize: 10,
                fontFamily: "'DM Mono', monospace",
                color: c.color,
              }}
            >
              {c.count}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
