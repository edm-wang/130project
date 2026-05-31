// [GenAI Usage] Prompt:
// Create a useFeedback React hook that fetches GET /recommendations/feedback and returns a Map
// from paper_id to feedback_value (1 or -1), so FeedPage can seed the initial vote state of
// each FeedPaperCard. Follow the same auth-guard and cancellation pattern as useSavedPapers —
// skip the fetch in mock mode or when auth is not ready, and silently ignore errors since vote
// state is non-critical (buttons just initialise to 0).
// [GenAI Usage] Response begins:
import { useEffect, useState } from 'react';

import useAuth from '../../hooks/useAuth.js';
import { fetchFeedback, isMockMode } from '../../lib/api.js';

/**
 * Fetches the current user's recommendation feedback (upvotes/downvotes) and
 * returns a Map from paper_id → feedback_value (1 or -1).
 *
 * @returns {{ voteByPaperId: Map<string, number> }}
 */
export default function useFeedback() {
  const auth = useAuth();
  const accessToken = auth.session ? auth.session.access_token : '';

  const [voteByPaperId, setVoteByPaperId] = useState(new Map());

  useEffect(() => {
    let cancelled = false;

    if (isMockMode() || auth.status === 'loading' || auth.status === 'signed-out' || auth.status === 'unconfigured') {
      return undefined;
    }

    fetchFeedback()
      .then((data) => {
        if (cancelled) return;
        const map = new Map(
          (data.feedback || []).map((row) => [row.paper_id, row.feedback_value]),
        );
        setVoteByPaperId(map);
      })
      .catch(() => {
        // Non-critical — vote buttons just initialise to 0.
      });

    return () => { cancelled = true; };
  }, [auth.status, accessToken]);

  return { voteByPaperId };
}
// [GenAI Usage] Response ends
// [GenAI Reflection] I used Claude Code to generate this hook because it is structurally
// identical to useSavedPapers — same auth guard, same cancellation flag, same dependency
// array — and generating it manually would risk subtle divergence from that established
// pattern. I verified that the Map is built from paper_id (string) keys matching the
// rec.paper_id values passed in FeedPage, and that errors are silently swallowed since
// a missing vote state is non-critical: buttons simply initialise to 0 and the user can
// re-vote without data loss.
