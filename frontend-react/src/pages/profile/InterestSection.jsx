import InterestTag from '../../components/atoms/InterestTag.jsx';
import styles from './InterestSection.module.css';

/**
 * @param {Object} props
 * @param {string} props.label
 * @param {'field'|'topic'|'author'|'keyword'} props.kind
 * @param {string[]} props.values
 * @param {(value: string) => void} [props.onRemove]
 */
export default function InterestSection({ label, kind, values, onRemove }) {
  return (
    <div className={styles.section}>
      <div className={styles.label}>{label}</div>
      <div className={styles.grid}>
        {values.map((v) => (
          <InterestTag
            key={v}
            kind={kind}
            removable
            onRemove={onRemove ? () => onRemove(v) : undefined}
          >
            {v}
          </InterestTag>
        ))}
      </div>
    </div>
  );
}
