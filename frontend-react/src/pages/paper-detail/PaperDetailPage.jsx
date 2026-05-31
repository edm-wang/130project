// [GenAI Usage] Prompt:
// Rewrite PaperDetailPage to fetch real paper data from GET /papers/:id, fetch any existing
// summary from GET /papers/:id/summary (404 → show a "Generate" button), and seed vote/saved
// state from the useFeedback and useSavedPapers hooks via useEffect. Use independent cancelled
// flags per fetch effect to avoid stale-state races. Pass vote/saved as controlled props to
// PaperHeader so PaperDetailPage owns the state and the seeding effects can update it without
// re-mounting the header. Simplify the sidebar to ShareCard + a "Related papers coming soon"
// widget, removing all mock-specific sidebar cards.
// [GenAI Usage] Response begins:
import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';

import Widget from '../../components/widgets/Widget.jsx';
import { fetchPaper, fetchPaperSummary, generatePaperSummary } from '../../lib/api.js';
import useFeedback from '../feed/useFeedback.js';
import useSavedPapers from '../reading-list/useSavedPapers.js';
import PaperHeader from './PaperHeader.jsx';
import { ShareCard } from './SidebarCards.jsx';
import SummaryTabs from './SummaryTabs.jsx';
import TextSummary from './TextSummary.jsx';
import styles from './PaperDetailPage.module.css';

export default function PaperDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [tab, setTab] = useState(searchParams.get('tab') || 'abstract');

  const [paper, setPaper] = useState(null);
  const [paperStatus, setPaperStatus] = useState('loading');

  const [summary, setSummary] = useState(null);
  // idle | loading | ready | not-found | error
  const [summaryStatus, setSummaryStatus] = useState('idle');

  const { voteByPaperId } = useFeedback();
  const { savedPapers } = useSavedPapers();

  // Local vote/saved — seeded from global state once available
  const [vote, setVote] = useState(0);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setPaper(null);
    setPaperStatus('loading');
    fetchPaper(id)
      .then((data) => {
        if (cancelled) return;
        setPaper(data.paper);
        setPaperStatus('ready');
      })
      .catch((err) => {
        if (cancelled) return;
        setPaperStatus(err?.code === 'NOT_FOUND' ? 'not-found' : 'error');
      });
    return () => { cancelled = true; };
  }, [id]);

  useEffect(() => {
    let cancelled = false;
    setSummary(null);
    setSummaryStatus('idle');
    fetchPaperSummary(id)
      .then((data) => {
        if (cancelled) return;
        setSummary(data.summary);
        setSummaryStatus('ready');
      })
      .catch((err) => {
        if (cancelled) return;
        setSummaryStatus(err?.code === 'NOT_FOUND' ? 'not-found' : 'error');
      });
    return () => { cancelled = true; };
  }, [id]);

  // Seed vote/saved state when global data arrives
  useEffect(() => {
    if (paper?.id) setVote(voteByPaperId.get(paper.id) ?? 0);
  }, [paper?.id, voteByPaperId]);

  useEffect(() => {
    if (paper?.id) setSaved(savedPapers.some((p) => p.id === paper.id));
  }, [paper?.id, savedPapers]);

  async function handleGenerateSummary() {
    setSummaryStatus('loading');
    try {
      const data = await generatePaperSummary(id);
      setSummary(data.summary);
      setSummaryStatus('ready');
    } catch {
      setSummaryStatus('error');
    }
  }

  return (
    <div>
      <h2 className="sr-only">Paper detail</h2>

      <div className={styles.breadcrumb}>
        <button type="button" className="link" onClick={() => navigate(-1)}>
          ← Back
        </button>
        <span>/</span>
        <Link to="/feed" className="link">
          Today's Feed
        </Link>
        <span>/</span>
        <span style={{ color: 'var(--color-text-primary)' }}>Paper detail</span>
      </div>

      {paperStatus === 'loading' && (
        <div className={styles.status}>Loading paper…</div>
      )}
      {paperStatus === 'not-found' && (
        <div className={styles.status}>Paper not found.</div>
      )}
      {paperStatus === 'error' && (
        <div className={styles.status}>Could not load paper.</div>
      )}

      {paperStatus === 'ready' && paper && (
        <div className={styles.body}>
          <div>
            <PaperHeader
              paper={paper}
              vote={vote}
              setVote={setVote}
              saved={saved}
              setSaved={setSaved}
            />

            <div className={styles.card}>
              <SummaryTabs active={tab} onChange={setTab} />

              {tab === 'abstract' && (
                <div
                  style={{
                    fontSize: 13,
                    color: 'var(--color-text-secondary)',
                    lineHeight: 1.8,
                  }}
                >
                  {paper.abstract || 'No abstract available.'}
                </div>
              )}

              {tab === 'text' && (
                <>
                  {summaryStatus === 'loading' && (
                    <div style={{ fontSize: 13, color: 'var(--color-text-tertiary)', padding: '12px 0' }}>
                      Generating summary…
                    </div>
                  )}
                  {summaryStatus === 'ready' && summary && (
                    <TextSummary summary={summary} onRegenerate={handleGenerateSummary} />
                  )}
                  {(summaryStatus === 'not-found' || summaryStatus === 'idle' || summaryStatus === 'error') && (
                    <div style={{ padding: '12px 0' }}>
                      <div style={{ fontSize: 13, color: 'var(--color-text-tertiary)', marginBottom: 12 }}>
                        {summaryStatus === 'error'
                          ? 'Summary generation failed.'
                          : 'No summary yet.'}
                      </div>
                      <button
                        type="button"
                        className={styles.generateBtn}
                        onClick={handleGenerateSummary}
                      >
                        ✦ Generate AI summary
                      </button>
                    </div>
                  )}
                </>
              )}

              {tab === 'video' && (
                <div style={{ fontSize: 13, color: 'var(--color-text-tertiary)', padding: '12px 0' }}>
                  Video summary coming soon.
                </div>
              )}
            </div>
          </div>

          <aside>
            <ShareCard paper={paper} />
            <Widget title="Related papers">
              <div style={{ fontSize: 12, color: 'var(--color-text-tertiary)' }}>
                Coming soon.
              </div>
            </Widget>
          </aside>
        </div>
      )}
    </div>
  );
}
// [GenAI Usage] Response ends
// [GenAI Reflection] I used Claude Code to rewrite this page because it required coordinating
// four independent async data sources (paper, summary, feedback, saved papers) without any of
// them blocking the others, while keeping vote/saved state correctly seeded as each arrives.
// The two seeding useEffects (paper?.id + voteByPaperId, paper?.id + savedPapers) are the key
// design decision: they decouple the paper fetch from the auth-dependent hooks so the header
// renders correctly whether those hooks resolve before or after the paper loads. I verified
// that the cancelled flag pattern is applied to both the paper and summary fetches independently,
// preventing stale setState calls if the user navigates away mid-flight.
