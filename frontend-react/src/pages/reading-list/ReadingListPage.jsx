// [GenAI Usage] Prompt:
// Rewire ReadingListPage to replace all mock data imports with the useSavedPapers hook.
// Implement functional tab switching: Reading List tab shows real data with status messages,
// Digest Video tab shows a "coming soon" placeholder. Derive filter chips and category counts
// from the live savedPapers array. Replace the stats widget with "coming soon".
// [GenAI Usage] Response Starts:
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import PageTabs from '../../components/chrome/PageTabs.jsx';
import Badge from '../../components/atoms/Badge.jsx';
import Widget from '../../components/widgets/Widget.jsx';
import { unsavePaper } from '../../lib/api.js';

import ReadingListFilters from './ReadingListFilters.jsx';
import ReadingListRow from './ReadingListRow.jsx';
import useSavedPapers from './useSavedPapers.js';
import styles from './ReadingListPage.module.css';

const PAGE_TABS = [
  { id: 'list', label: 'Reading List' },
  { id: 'digest', label: "Today's Digest Video" },
];

export default function ReadingListPage() {
  const navigate = useNavigate();
  const [pageTab, setPageTab] = useState('list');
  const [filter, setFilter] = useState('All');

  const { status, savedPapers, filterChips, error, removePaper } = useSavedPapers();

  async function handleRemove(paperId) {
    removePaper(paperId);
    try {
      await unsavePaper(paperId);
    } catch {
      // optimistic removal; silently ignore if backend call fails
    }
  }

  const filtered = savedPapers.filter((p) => {
    if (filter === 'All') return true;
    if (filter === 'Unread') return !p.read;
    return p.categories.includes(filter);
  });

  // Derive category counts from live data for the sidebar widget.
  const categoryCounts = Object.entries(
    savedPapers
      .flatMap((p) => p.categories)
      .reduce((acc, c) => { acc[c] = (acc[c] || 0) + 1; return acc; }, {}),
  ).map(([label, count]) => ({ label, count }));

  return (
    <div>
      <h2 className="sr-only">
        Paper Aggregator — reading list and daily feed digest video
      </h2>

      <PageTabs tabs={PAGE_TABS} active={pageTab} onChange={setPageTab} />

      <div className={styles.body}>
        <div>
          {/* READING LIST TAB */}
          {pageTab === 'list' && (
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <div className={styles.cardTitle}>
                  Reading List · {savedPapers.length} papers
                </div>
                <button type="button" className={styles.cardAction}>
                  Sort by date ↕
                </button>
              </div>

              <ReadingListFilters
                chips={filterChips}
                active={filter}
                onChange={setFilter}
              />

              {status === 'loading' && (
                <div className={styles.status}>Loading reading list…</div>
              )}
              {status === 'no-token' && (
                <div className={styles.status}>{error}</div>
              )}
              {status === 'network-error' && (
                <div className={styles.status}>
                  {error} Start it with{' '}
                  <code>cd backend && uvicorn app.main:app --reload</code>.
                </div>
              )}
              {status === 'unauthorized' && (
                <div className={styles.status}>
                  Your session expired. Try signing out and back in.
                </div>
              )}
              {status === 'error' && (
                <div className={styles.status}>Could not load reading list: {error}</div>
              )}
              {status === 'ready' && savedPapers.length === 0 && (
                <div className={styles.status}>No saved papers yet.</div>
              )}

              {filtered.map((paper, i) => (
                <ReadingListRow
                  key={paper.id}
                  paper={paper}
                  index={i}
                  onOpen={() => paper.sourceUrl ? window.open(paper.sourceUrl, '_blank', 'noopener,noreferrer') : navigate(`/papers/${paper.id}`)}
                  onTextSummary={() => navigate(`/papers/${paper.id}?tab=text`)}
                  onRemove={() => handleRemove(paper.id)}
                />
              ))}
            </div>
          )}

          {/* DIGEST VIDEO TAB — coming soon */}
          {pageTab === 'digest' && (
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <div className={styles.cardTitle}>▶ Today's Feed — Digest Video</div>
              </div>
              <div style={{ fontSize: 13, color: 'var(--color-text-tertiary)', padding: '12px 0' }}>
                Digest video coming soon.
              </div>
            </div>
          )}
        </div>

        {/* RIGHT SIDEBAR */}
        <aside>
          <Widget title="Reading List Stats">
            <div style={{ fontSize: 13, color: 'var(--color-text-tertiary)', padding: '8px 0' }}>
              Stats coming soon.
            </div>
          </Widget>

          <Widget title="Categories">
            {categoryCounts.length === 0 ? (
              <div style={{ fontSize: 12, color: 'var(--color-text-tertiary)' }}>
                No categories yet.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
                {categoryCounts.map((c) => (
                  <div
                    key={c.label}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <Badge variant="cat" style={{ fontSize: 12, padding: '3px 9px' }}>
                      {c.label}
                    </Badge>
                    <span style={{ fontSize: 12, color: 'var(--color-text-tertiary)' }}>
                      {c.count} paper{c.count === 1 ? '' : 's'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </Widget>

          <Widget title="Digest Video">
            <div style={{ fontSize: 13, color: 'var(--color-text-tertiary)', padding: '8px 0' }}>
              Coming soon.
            </div>
          </Widget>
        </aside>
      </div>
    </div>
  );
}
// [GenAI Usage] Response Ends
// [GenAI Usage] Reflection:
// I used Claude Code for this rewrite because it required removing a large block of digest video
// JSX, wiring the useSavedPapers hook, and converting the always-rendered layout into a
// tab-conditional one simultaneously. I verified the categoryCounts derivation uses reduce
// correctly and handles papers with multiple categories, and confirmed that the filter logic
// (filter === 'Unread' returns !p.read) is unchanged from the original mock implementation
// so existing behaviour is preserved when switching to live data.
// Later extended to wire up the action buttons on each ReadingListRow: added useNavigate so
// onOpen and onTextSummary can push /papers/:id and /papers/:id?tab=text without the row
// needing to know about routing, and added handleRemove which does an optimistic delete —
// removePaper runs first so the UI updates instantly, then unsavePaper fires the DELETE in the
// background. I decided to silently swallow errors on the backend call since a failed unsave
// is low stakes and re-fetching the whole list just to re-add one row felt like overkill.
// Later changed onOpen to open paper.sourceUrl (the arXiv link stored on the backend) in a
// new tab instead of navigating internally, with a fallback to /papers/:id if no URL is set.
