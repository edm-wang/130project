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
import {
  quickLinks,
  similarResearchers,
  userInterests,
  weekStats,
} from './mockData.js';
import styles from './FeedPage.module.css';

export default function FeedPage() {
  const { status, batch, recommendations, error } = useRecommendations();

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
              {userInterests.map((i) => (
                <InterestTag key={i.id} kind={i.interest_type}>
                  {i.value}
                </InterestTag>
              ))}
            </div>
            <button type="button" className={styles.addBtn}>
              + Add interest
            </button>
          </Widget>

          <LegendWidget />
          <EmailDigestWidget />
        </aside>

        {/* FEED ------------------------------------------------------------- */}
        <main className={styles.feed}>
          <FeedHeader batch={batch} count={recommendations.length} />

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
              No recommendations yet — generate a completed batch on the
              backend and reload.
            </div>
          ) : null}

          {recommendations.map((rec, idx) => (
            <FeedPaperCard key={rec.id} rec={rec} unread={idx < 2} />
          ))}

          {status === 'ready' && recommendations.length > 0 ? (
            <div className={styles.loadMore}>
              <button type="button" className={styles.loadMoreBtn}>
                Load more papers
              </button>
            </div>
          ) : null}
        </main>

        {/* RIGHT SIDEBAR ---------------------------------------------------- */}
        <aside className={styles.right}>
          <WeekStatsWidget stats={weekStats} />
          <SimilarResearchersWidget researchers={similarResearchers} />
          <QuickLinksWidget links={quickLinks} />
        </aside>
      </div>
    </div>
  );
}
