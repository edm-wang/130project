import styles from './PageTabs.module.css';

/**
 * @param {Object} props
 * @param {{ id: string, label: string }[]} props.tabs
 * @param {string} props.active id of the currently selected tab
 * @param {(id: string) => void} props.onChange
 */
export default function PageTabs({ tabs, active, onChange }) {
  return (
    <div className={styles.tabs}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          className={[styles.tab, active === tab.id ? styles.active : '']
            .join(' ')
            .trim()}
          onClick={() => onChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
