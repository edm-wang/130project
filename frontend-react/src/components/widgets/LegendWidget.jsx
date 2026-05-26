import InterestTag from '../atoms/InterestTag.jsx';
import Widget from './Widget.jsx';
import styles from './Widget.module.css';

const ROWS = [
  { kind: 'field', label: 'Field', hint: 'Broad area' },
  { kind: 'topic', label: 'Topic', hint: 'Specific topic' },
  { kind: 'author', label: 'Author', hint: 'Researcher' },
  { kind: 'keyword', label: 'Keyword', hint: 'Term' },
];

export default function LegendWidget() {
  return (
    <Widget title="Legend">
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {ROWS.map((row) => (
          <div key={row.kind} className={styles.legendRow}>
            <InterestTag kind={row.kind}>{row.label}</InterestTag>
            <span>{row.hint}</span>
          </div>
        ))}
      </div>
    </Widget>
  );
}
