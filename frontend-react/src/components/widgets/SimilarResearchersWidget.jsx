import Avatar from '../atoms/Avatar.jsx';
import Badge from '../atoms/Badge.jsx';
import Widget from './Widget.jsx';
import styles from './Widget.module.css';

/**
 * @param {Object} props
 * @param {{ initials: string, color: 'green'|'mint'|'lilac'|'peach', name: string, affil: string, shared: string }[]} props.researchers
 */
export default function SimilarResearchersWidget({ researchers }) {
  return (
    <Widget title="Similar Researchers">
      {researchers.map((r) => (
        <div key={r.name} className={styles.researcher}>
          <Avatar initials={r.initials} size="sm" color={r.color} />
          <div>
            <div className={styles.researcherName}>{r.name}</div>
            <div className={styles.researcherAffil}>{r.affil}</div>
            <Badge variant="shared" style={{ marginTop: 2 }}>
              {r.shared}
            </Badge>
          </div>
        </div>
      ))}
      <button type="button" className={styles.viewAllBtn}>
        View all →
      </button>
    </Widget>
  );
}
