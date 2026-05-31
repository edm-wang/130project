import { useState } from 'react';

import Badge from '../../components/atoms/Badge.jsx';
import PillButton from '../../components/atoms/PillButton.jsx';
import Widget from '../../components/widgets/Widget.jsx';
import styles from './SidebarCards.module.css';

export function SavedToReadingListCard({ paper }) {
  return (
    <Widget title="Saved to reading list">
      <div className={styles.catRow}>
        <div>
          <div
            style={{
              fontSize: 12,
              color: 'var(--color-text-secondary)',
              marginBottom: 5,
            }}
          >
            Auto-category
          </div>
          {paper.autoCategories.map((c, i) => (
            <Badge
              key={c}
              variant="cat"
              style={{ marginLeft: i === 0 ? 0 : 4 }}
            >
              {c}
            </Badge>
          ))}
        </div>
        <button type="button" className={styles.catEdit}>
          Edit
        </button>
      </div>
      <div
        style={{
          fontSize: 11,
          color: 'var(--color-text-tertiary)',
          marginTop: 8,
        }}
      >
        Saved {paper.savedDate} · Reading list · {paper.readingListSize} papers
      </div>
    </Widget>
  );
}

export function YourVoteCard({ paper }) {
  const [vote, setVote] = useState(paper.userVote || 0);
  return (
    <Widget title="Your vote">
      <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
        <PillButton
          variant="up"
          active={vote === 1}
          style={{ flex: 1, justifyContent: 'center' }}
          onClick={() => setVote(vote === 1 ? 0 : 1)}
        >
          ▲ {vote === 1 ? 'Upvoted' : 'Upvote'}
        </PillButton>
        <PillButton
          variant="down"
          active={vote === -1}
          style={{ flex: 1, justifyContent: 'center' }}
          onClick={() => setVote(vote === -1 ? 0 : -1)}
        >
          ▼
        </PillButton>
      </div>
      <div style={{ fontSize: 11, color: 'var(--color-text-tertiary)' }}>
        {paper.upvotes} upvotes · {paper.downvotes} downvotes from all users
      </div>
    </Widget>
  );
}

export function VideoSidebarCard({ video }) {
  return (
    <Widget title="Generate video summary">
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '10px 13px',
          borderRadius: 'var(--border-radius-md)',
          fontSize: 11,
          marginBottom: 10,
          background: '#E1F5EE',
          color: '#0F6E56',
        }}
      >
        <div
          style={{
            width: 7,
            height: 7,
            borderRadius: '50%',
            background: 'var(--color-brand)',
            flexShrink: 0,
          }}
        />
        Video ready
      </div>
      <div
        style={{
          fontSize: 11,
          color: 'var(--color-text-tertiary)',
          lineHeight: 1.6,
        }}
      >
        A {video.lengthLabel} narrated visual summary was auto-generated from the
        paper abstract and key sections.
      </div>
      <PillButton
        large
        style={{ width: '100%', justifyContent: 'center', marginTop: 10, fontSize: 12 }}
      >
        ▶ Watch video
      </PillButton>
    </Widget>
  );
}

export function ShareCard({ paper }) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(window.location.href).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }

  const emailHref = paper
    ? `mailto:?subject=${encodeURIComponent(paper.title)}&body=${encodeURIComponent(window.location.href)}`
    : 'mailto:';

  return (
    <Widget title="Share">
      <div className={styles.shareRow}>
        <button type="button" className={styles.shareBtn} onClick={handleCopy}>
          {copied ? 'Copied!' : 'Copy link'}
        </button>
        <a className={styles.shareBtn} href={emailHref}>
          Email
        </a>
        {paper?.source_url && (
          <a
            className={styles.shareBtn}
            href={paper.source_url}
            target="_blank"
            rel="noreferrer"
          >
            ↗ arXiv
          </a>
        )}
      </div>
    </Widget>
  );
}

export function RelatedPapersCard({ related }) {
  return (
    <Widget title="Related papers">
      {related.map((r) => (
        <div key={r.title} className={styles.similar}>
          <div className={styles.similarThumb}>{r.cat}</div>
          <div>
            <div className={styles.similarTitle}>{r.title}</div>
            <div className={styles.similarMeta}>{r.meta}</div>
          </div>
        </div>
      ))}
    </Widget>
  );
}
