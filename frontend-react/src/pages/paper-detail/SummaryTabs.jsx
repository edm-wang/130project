import styles from './SummaryTabs.module.css';

const TABS = [
  { id: 'text', label: '✦ AI Text Summary' },
  { id: 'video', label: '▶ Video Summary' },
  { id: 'abstract', label: 'Abstract' },
];

export default function SummaryTabs({ active, onChange }) {
  return (
    <div className={styles.tabRow}>
      {TABS.map((t) => (
        <button
          key={t.id}
          type="button"
          className={[styles.tab, active === t.id ? styles.active : '']
            .join(' ')
            .trim()}
          onClick={() => onChange(t.id)}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
