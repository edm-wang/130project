import { useNavigate } from 'react-router-dom';

import Badge from '../../components/atoms/Badge.jsx';
import styles from './ReadingListRow.module.css';

export default function ReadingListRow({ paper, index }) {
  const navigate = useNavigate();
  return (
    <div className={styles.row}>
      <div className={styles.num}>{index + 1}</div>
      <div className={styles.content}>
        <button
          type="button"
          className={styles.title}
          onClick={() => navigate(`/papers/${paper.id}`)}
        >
          {paper.title}
        </button>
        <div className={styles.meta}>{paper.meta}</div>
        <div className={styles.badges}>
          {paper.categories.map((c) => (
            <Badge key={c} variant="cat">
              {c}
            </Badge>
          ))}
          {paper.isNew ? <Badge variant="new">New</Badge> : null}
          {paper.read ? <Badge variant="read">Read</Badge> : null}
        </div>
        <div className={styles.actions}>
          <button type="button" className={styles.action}>
            ↗ Open
          </button>
          <button type="button" className={styles.action}>
            ✦ Text summary
          </button>
          <button type="button" className={styles.action}>
            Edit category
          </button>
          <button type="button" className={styles.action}>
            Remove
          </button>
        </div>
      </div>
    </div>
  );
}
