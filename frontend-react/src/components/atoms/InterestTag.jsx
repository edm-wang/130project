import styles from './InterestTag.module.css';

/**
 * @param {Object} props
 * @param {'field'|'topic'|'author'|'keyword'|'category'} props.kind
 * @param {React.ReactNode} props.children
 * @param {boolean} [props.removable]
 * @param {() => void} [props.onRemove]
 */
export default function InterestTag({ kind, children, removable, onRemove }) {
  // `category` falls back to keyword styling to keep the same visual hierarchy.
  const variantClass = styles[kind] ?? styles.keyword;
  return (
    <span className={[styles.tag, variantClass].join(' ')}>
      {children}
      {removable ? (
        <button
          type="button"
          className={styles.remove}
          onClick={onRemove}
          aria-label="Remove interest"
        >
          ×
        </button>
      ) : null}
    </span>
  );
}
