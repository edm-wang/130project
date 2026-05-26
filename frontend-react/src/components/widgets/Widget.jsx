import styles from './Widget.module.css';

/**
 * Shared widget shell with an uppercase title and rounded card chrome.
 */
export default function Widget({ title, children, action }) {
  return (
    <div className={styles.widget}>
      <div
        className={styles.title}
        style={
          action
            ? { display: 'flex', justifyContent: 'space-between', alignItems: 'center' }
            : undefined
        }
      >
        <span>{title}</span>
        {action}
      </div>
      {children}
    </div>
  );
}
