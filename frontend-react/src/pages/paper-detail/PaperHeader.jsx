import { useState } from 'react';

import PillButton from '../../components/atoms/PillButton.jsx';
import styles from './PaperHeader.module.css';

export default function PaperHeader({ paper }) {
  const [vote, setVote] = useState(paper.userVote || 0);
  const [saved, setSaved] = useState(Boolean(paper.userSaved));

  return (
    <div className={styles.card}>
      <div className={styles.source}>
        {paper.source} · {paper.category} · {paper.publishedAt}
      </div>
      <div className={styles.title}>{paper.title}</div>
      <div className={styles.authors}>{paper.authors}</div>
      <div className={styles.affil}>{paper.affiliation}</div>

      <div className={styles.metaRow}>
        {paper.metaPills.map((p) => (
          <span key={p} className={styles.metaPill}>
            {p}
          </span>
        ))}
      </div>

      <div className={styles.reason}>
        <strong style={{ fontWeight: 500 }}>Why recommended:</strong> {paper.reason}
      </div>

      <div className={styles.actionRow}>
        <PillButton
          variant="up"
          large
          active={vote === 1}
          onClick={() => setVote(vote === 1 ? 0 : 1)}
        >
          ▲ Upvote
          <span className={styles.voteCount}>
            {paper.upvotes + (vote === 1 ? 1 : 0)}
          </span>
        </PillButton>
        <PillButton
          variant="down"
          large
          active={vote === -1}
          onClick={() => setVote(vote === -1 ? 0 : -1)}
        >
          ▼ Downvote
          <span className={styles.voteCount}>
            {paper.downvotes + (vote === -1 ? 1 : 0)}
          </span>
        </PillButton>
        <PillButton
          variant="save"
          large
          active={saved}
          onClick={() => setSaved(!saved)}
        >
          {saved ? '★ Saved' : '☆ Save'}
        </PillButton>
        <PillButton variant="arxiv" large href={paper.sourceUrl}>
          ↗ Open on arXiv
        </PillButton>
      </div>
    </div>
  );
}
