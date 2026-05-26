import { useNavigate } from 'react-router-dom';

import Badge from '../../components/atoms/Badge.jsx';
import styles from './SavedPaperRow.module.css';

export default function SavedPaperRow({ paper }) {
  const navigate = useNavigate();
  return (
    <div className={styles.row}>
      <button
        type="button"
        className={styles.title}
        onClick={() => navigate(`/papers/${paper.id}`)}
      >
        {paper.title}
      </button>
      <div className={styles.meta}>{paper.meta}</div>
      <div>
        {paper.categories.map((cat) => (
          <Badge key={cat} variant="cat" style={{ marginRight: 4 }}>
            {cat}
          </Badge>
        ))}
      </div>
      <div className={styles.actions}>
        <button type="button" className={styles.action}>
          ↗ Open
        </button>
        <button type="button" className={styles.action}>
          ✦ Summary
        </button>
        <button type="button" className={styles.action}>
          Edit category
        </button>
      </div>
    </div>
  );
}
