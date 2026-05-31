// [GenAI Usage] Prompt:
// Rewrite PaperHeader to accept the real paper shape from the API (title, authors_text, source,
// categories array, published_at, source_url) instead of the mock shape. Receive vote/setVote
// and saved/setSaved as controlled props from PaperDetailPage. Wire the upvote, downvote, and
// save buttons to the feedback and saved-papers API using the same optimistic-update-plus-revert
// pattern already established in FeedPaperCard. Remove affiliation, metaPills, reason, and
// aggregate vote counts — none of these exist in the real data.
// [GenAI Usage] Response begins:
import PillButton from '../../components/atoms/PillButton.jsx';
import { deleteFeedback, postFeedback, savePaper, unsavePaper } from '../../lib/api.js';
import { formatShortDate } from '../../lib/format.js';
import styles from './PaperHeader.module.css';

export default function PaperHeader({ paper, vote, setVote, saved, setSaved }) {
  const category =
    Array.isArray(paper.categories) && paper.categories.length ? paper.categories[0] : '';
  const sourceLine = [paper.source, category, formatShortDate(paper.published_at)]
    .filter(Boolean)
    .join(' · ');

  return (
    <div className={styles.card}>
      <div className={styles.source}>{sourceLine}</div>
      <div className={styles.title}>{paper.title}</div>
      <div className={styles.authors}>{paper.authors_text || 'Unknown authors'}</div>

      <div className={styles.actionRow}>
        <PillButton
          variant="up"
          large
          active={vote === 1}
          onClick={async () => {
            const next = vote === 1 ? 0 : 1;
            setVote(next);
            try {
              if (next === 0) await deleteFeedback(paper.id);
              else await postFeedback(paper.id, next);
            } catch {
              setVote(vote);
            }
          }}
        >
          ▲ Upvote
        </PillButton>
        <PillButton
          variant="down"
          large
          active={vote === -1}
          onClick={async () => {
            const next = vote === -1 ? 0 : -1;
            setVote(next);
            try {
              if (next === 0) await deleteFeedback(paper.id);
              else await postFeedback(paper.id, next);
            } catch {
              setVote(vote);
            }
          }}
        >
          ▼ Downvote
        </PillButton>
        <PillButton
          variant="save"
          large
          active={saved}
          onClick={async () => {
            const next = !saved;
            setSaved(next);
            try {
              if (next) await savePaper(paper.id);
              else await unsavePaper(paper.id);
            } catch {
              setSaved(!next);
            }
          }}
        >
          {saved ? '★ Saved' : '☆ Save'}
        </PillButton>
        {paper.source_url && (
          <PillButton variant="arxiv" large href={paper.source_url}>
            ↗ Open on arXiv
          </PillButton>
        )}
      </div>
    </div>
  );
}
// [GenAI Usage] Response ends
// [GenAI Reflection] Receiving vote/saved as controlled props (rather than seeding useState
// internally) was the right call here: it lets PaperDetailPage run the seeding useEffects
// once and update the header without forcing a remount. The optimistic-update pattern is
// identical to FeedPaperCard, so I verified the revert uses the captured pre-click value
// of vote (or saved) in each closure, not a re-read of the prop, which would be stale after
// the optimistic setVote/setSaved call.
