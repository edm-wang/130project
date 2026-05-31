import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import PillButton from '../../components/atoms/PillButton.jsx';
import { deleteFeedback, postFeedback, savePaper, unsavePaper } from '../../lib/api.js';
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

      {/* [GenAI Usage] Prompt: Wire the upvote and downvote buttons to the feedback API.
          Clicking an active vote should remove it (toggle to 0 via DELETE). Clicking the
          opposite vote should switch directly. Use optimistic update + revert on error,
          same pattern as the save button. */}
      {/* [GenAI Usage] Response begins: */}
      <div className={styles.actions}>
        <PillButton
          variant="up"
          active={vote === 1}
          onClick={async () => {
            const next = vote === 1 ? 0 : 1;
            setVote(next);
            try {
              if (next === 0) await deleteFeedback(rec.paper_id);
              else await postFeedback(rec.paper_id, next);
            } catch {
              setVote(vote);
            }
          }}
        >
          ▲
        </PillButton>
        <PillButton
          variant="down"
          active={vote === -1}
          onClick={async () => {
            const next = vote === -1 ? 0 : -1;
            setVote(next);
            try {
              if (next === 0) await deleteFeedback(rec.paper_id);
              else await postFeedback(rec.paper_id, next);
            } catch {
              setVote(vote);
            }
          }}
        >
          ▼
        </PillButton>
        {/* [GenAI Usage] Response ends */}
        {/* [GenAI Reflection] The toggle logic captures the current `vote` in the closure so
            the revert always restores the correct prior value even if the component re-renders
            before the await resolves. Switching directly from upvote to downvote (or vice versa)
            calls POST rather than DELETE, since the backend upserts on conflict, so no intermediate
            removal step is needed. */}
        <PillButton variant="summary" onClick={() => navigate(`/papers/${rec.paper_id}?tab=text`)}>✦ Summarize</PillButton>
        <PillButton variant="ghost" href={link}>
          ↗ {linkLabel}
        </PillButton>
        {/* [GenAI Usage] Prompt: Wire the Save button to POST /saved-papers (save) and
            DELETE /saved-papers/:id (unsave). Use optimistic local state — flip immediately
            and revert on error — following the same pattern as the vote buttons above. */}
        {/* [GenAI Usage] Response begins: */}
        <span className={styles.saveSlot}>
          <PillButton
            variant="save"
            active={saved}
            onClick={async () => {
              const next = !saved;
              setSaved(next);
              try {
                if (next) {
                  await savePaper(rec.paper_id);
                } else {
                  await unsavePaper(rec.paper_id);
                }
              } catch {
                setSaved(!next);
              }
            }}
          >
            {saved ? '★ Saved' : '☆ Save'}
          </PillButton>
        </span>
        {/* [GenAI Usage] Response ends */}
        {/* [GenAI Reflection] The optimistic update pattern (flip state → call API → revert on
            catch) keeps the UI snappy without a loading state. I verified the revert path uses
            the captured `next` value rather than re-reading `saved`, so it is correct even if
            the component re-renders during the await. I also confirmed that `savePaper` and
            `unsavePaper` use the shared `apiFetch` helper, so auth errors bubble up correctly
            and the revert fires for any thrown error, not just network failures. */}
      </div>
    </div>
  );
}
