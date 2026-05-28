import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import PillButton from '../../components/atoms/PillButton.jsx';
import { formatShortDate } from '../../lib/format.js';
import ReasonBox from './ReasonBox.jsx';
import styles from './FeedPaperCard.module.css';

/**
 * @param {Object} props
 * @param {import('../../shapes/shapes.js').Recommendation} props.rec
 * @param {boolean} [props.unread]
 */
export default function FeedPaperCard({ rec, unread }) {
  const navigate = useNavigate();
  const paper = rec.paper || {};

  // Local UI state for vote/save. Module-level store could lift this later.
  const [vote, setVote] = useState(rec.user_vote || 0); // -1, 0, +1
  const [saved, setSaved] = useState(Boolean(rec.user_saved));

  const sourceLine = [
    paper.source,
    Array.isArray(paper.categories) && paper.categories.length ? paper.categories[0] : '',
    formatShortDate(paper.published_at),
  ]
    .filter(Boolean)
    .join(' · ');

  const link = paper.source_url || paper.pdf_url || '#';
  const linkLabel = paper.source || 'Open';

  return (
    <div className={[styles.paper, unread ? styles.unread : ''].join(' ').trim()}>
      <div className={styles.source}>{sourceLine}</div>
      <button
        type="button"
        className={styles.title}
        onClick={() => navigate(`/papers/${rec.paper_id}`)}
      >
        {paper.title || 'Untitled paper'}
      </button>
      <div className={styles.authors}>{paper.authors_text || 'Unknown authors'}</div>
      {paper.abstract ? <div className={styles.abstract}>{paper.abstract}</div> : null}
      {rec.explanation_summary ? <ReasonBox>{rec.explanation_summary}</ReasonBox> : null}

      <div className={styles.actions}>
        <PillButton
          variant="up"
          active={vote === 1}
          onClick={() => setVote(vote === 1 ? 0 : 1)}
        >
          ▲
        </PillButton>
        <PillButton
          variant="down"
          active={vote === -1}
          onClick={() => setVote(vote === -1 ? 0 : -1)}
        >
          ▼
        </PillButton>
        <PillButton variant="summary">✦ Summarize</PillButton>
        <PillButton variant="ghost" href={link}>
          ↗ {linkLabel}
        </PillButton>
        <span className={styles.saveSlot}>
          <PillButton variant="save" active={saved} onClick={() => setSaved(!saved)}>
            {saved ? '★ Saved' : '☆ Save'}
          </PillButton>
        </span>
      </div>
    </div>
  );
}
