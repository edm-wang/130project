import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import InterestTag from '../../components/atoms/InterestTag.jsx';
import EmailDigestWidget from '../../components/widgets/EmailDigestWidget.jsx';
import LegendWidget from '../../components/widgets/LegendWidget.jsx';
import QuickLinksWidget from '../../components/widgets/QuickLinksWidget.jsx';
import SimilarResearchersWidget from '../../components/widgets/SimilarResearchersWidget.jsx';
import WeekStatsWidget from '../../components/widgets/WeekStatsWidget.jsx';
import Widget from '../../components/widgets/Widget.jsx';

import FeedHeader from './FeedHeader.jsx';
import FeedPaperCard from './FeedPaperCard.jsx';
import useRecommendations from './useRecommendations.js';
import { quickLinks, similarResearchers, weekStats } from './mockData.js';
import useInterests from '../profile/useInterests.js';
import useProfile from '../profile/useProfile.js';
import useSavedPapers from '../reading-list/useSavedPapers.js';
import useFeedback from './useFeedback.js';
import { isMockMode } from '../../lib/api.js';
import styles from './FeedPage.module.css';

export default function FeedPage() {
  const navigate = useNavigate();
  const { status: profileStatus } = useProfile();
  const { status, batch, recommendations, error } = useRecommendations({
    enabled: profileStatus !== 'loading' && profileStatus !== 'no-profile',
  });
  const { interests } = useInterests();
  const { savedPapers } = useSavedPapers();
  const savedPaperIds = new Set(savedPapers.map((p) => p.id));
  const { voteByPaperId } = useFeedback();

  // [GenAI Usage] Prompt: add client-side pagination to the feed — show PAGE_SIZE papers at a time,
  // wire the existing "Load more" button to reveal the next page, and reset when a new batch loads.
  // [GenAI Usage] Response begins:
  const PAGE_SIZE = 10;
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  // Reset pagination when a new batch loads.
  useEffect(() => {
    setVisibleCount(PAGE_SIZE);
  }, [batch?.id]);
  // [GenAI Usage] Response ends

  return (
    <div>
      <h2 className="sr-only">
        Paper Aggregator — personalized research feed dashboard
      </h2>

      <div className={styles.body}>
        {/* LEFT SIDEBAR ------------------------------------------------------ */}
        <aside className={styles.sidebar}>
          <Widget title="Research Interests">
            <div>
              {interests.length === 0 ? (
                <div style={{ fontSize: 12, color: 'var(--color-text-tertiary)' }}>
                  No interests yet. Add some on your profile.
                </div>
              ) : (
                interests.map((i) => (
                  <InterestTag key={i.id} kind={i.interest_type}>
                    {i.value}
                  </InterestTag>
                ))
              )}
            </div>
            <button
              type="button"
              className={styles.addBtn}
              onClick={() => navigate('/profile?tab=interests')}
            >
              + Add interest
            </button>
          </Widget>

          <LegendWidget />
          {isMockMode() ? (
            <EmailDigestWidget />
          ) : (
            <Widget title="Email Digest">
              <div style={{ fontSize: 12, color: 'var(--color-text-tertiary)', padding: '4px 0' }}>
                Coming soon.
              </div>
            </Widget>
          )}
        </aside>

        {/* FEED ------------------------------------------------------------- */}
        <main className={styles.feed}>
          <FeedHeader batch={batch} count={recommendations.length} />

          {profileStatus === 'no-profile' ? (
            <div className={styles.status}>
              Complete your profile to get personalized recommendations.{' '}
              <button
                type="button"
                className={styles.addBtn}
                onClick={() => navigate('/profile?tab=edit')}
              >
                Set up profile →
              </button>
            </div>
          ) : null}

          {status === 'loading' ? (
            <div className={styles.status}>Loading recommendations…</div>
          ) : null}

          {status === 'no-token' ? (
            <div className={styles.status}>{error}</div>
          ) : null}

          {status === 'network-error' ? (
            <div className={styles.status}>
              {error} Start it with{' '}
              <code>cd backend && uvicorn app.main:app --reload</code>.
            </div>
          ) : null}

          {status === 'unauthorized' ? (
            <div className={styles.status}>
              Your session expired or the backend rejected the token. Try
              signing out and back in.
            </div>
          ) : null}

          {status === 'error' ? (
            <div className={styles.status}>
              Could not load recommendations: {error}
            </div>
          ) : null}

          {status === 'ready' && recommendations.length === 0 ? (
            <div className={styles.status}>
              {interests.length === 0 ? (
                <>
                  Add research interests to your profile to get personalized recommendations.{' '}
                  <button
                    type="button"
                    className={styles.addBtn}
                    onClick={() => navigate('/profile?tab=interests')}
                  >
                    Add interests →
                  </button>
                </>
              ) : (
                'No recommendations yet — reload to generate your first batch.'
              )}
            </div>
          ) : null}

          {/* [GenAI Usage] Response begins (pagination render) */}
          {recommendations.slice(0, visibleCount).map((rec, idx) => (
            <FeedPaperCard
              key={rec.id}
              rec={{
                ...rec,
                user_saved: savedPaperIds.has(rec.paper_id),
                user_vote: voteByPaperId.get(rec.paper_id) ?? 0,
              }}
              unread={idx < 2}
            />
          ))}

          {status === 'ready' && visibleCount < recommendations.length ? (
            <div className={styles.loadMore}>
              <button
                type="button"
                className={styles.loadMoreBtn}
                onClick={() => setVisibleCount((c) => c + PAGE_SIZE)}
              >
                Load more papers
              </button>
            </div>
          ) : null}
          {/* [GenAI Usage] Response ends */}
          {/* [GenAI Reflection] The pagination logic is straightforward — visibleCount slices the
              already-loaded recommendations array, and the useEffect reset on batch?.id ensures the
              page resets when fresh recommendations arrive. I verified the button hides correctly
              when all papers are visible. */}
        </main>

        {/* RIGHT SIDEBAR ---------------------------------------------------- */}
        <aside className={styles.right}>
          {isMockMode() ? (
            <>
              <WeekStatsWidget stats={weekStats} />
              <SimilarResearchersWidget researchers={similarResearchers} />
              <QuickLinksWidget links={quickLinks} />
            </>
          ) : (
            <>
              <Widget title="This Week">
                <div style={{ fontSize: 12, color: 'var(--color-text-tertiary)', padding: '4px 0' }}>
                  Coming soon.
                </div>
              </Widget>
              <Widget title="Similar Researchers">
                <div style={{ fontSize: 12, color: 'var(--color-text-tertiary)', padding: '4px 0' }}>
                  Coming soon.
                </div>
              </Widget>
              <Widget title="Quick Links">
                <div style={{ fontSize: 12, color: 'var(--color-text-tertiary)', padding: '4px 0' }}>
                  Coming soon.
                </div>
              </Widget>
            </>
          )}
        </aside>
      </div>
    </div>
  );
}
