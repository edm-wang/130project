// [GenAI Usage] Prompt: The original HTML pages had a row of tab buttons at the top of the
// reading list (Digest / List / Themes) and the profile page (Interests / Saved / Settings),
// both styled the same way but with totally different tab lists. Make a generic tabs component
// that takes a list of {id, label} objects, an active id, and an onChange callback, so both
// pages can reuse it instead of each having their own copy of the tab markup and active-state
// styling logic.
// [GenAI Usage] Response Starts:
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
// [GenAI Usage] Response Ends
// [GenAI Reflection] I used Claude Code for this because the className-joining logic
// ([styles.tab, active === tab.id ? styles.active : ''].join(' ').trim()) is a pattern I copy
// around a lot but always second-guess the trim(). Without it you can end up with a trailing
// space in the class attribute when the tab isn't active, which doesn't break anything visually
// but looked sloppy in devtools. Both ReadingListPage and ProfilePage now pass their own tabs
// array into this component and keep their own "active tab" state, so PageTabs itself stays
// dumb and reusable.
