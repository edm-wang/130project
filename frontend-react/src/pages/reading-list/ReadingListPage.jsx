import { useState } from 'react';

import PageTabs from '../../components/chrome/PageTabs.jsx';
import Badge from '../../components/atoms/Badge.jsx';
import Widget from '../../components/widgets/Widget.jsx';
import widgetStyles from '../../components/widgets/Widget.module.css';

import DigestVideo from './DigestVideo.jsx';
import ReadingListFilters from './ReadingListFilters.jsx';
import ReadingListRow from './ReadingListRow.jsx';
import {
  TOTAL_SECONDS,
  categoryCounts,
  chapters,
  filterChips,
  readingList,
  slides,
  stats,
} from './mockData.js';
import styles from './ReadingListPage.module.css';

const PAGE_TABS = [
  { id: 'list', label: 'Reading List' },
  { id: 'digest', label: "Today's Digest Video" },
];

export default function ReadingListPage() {
  const [pageTab, setPageTab] = useState('list');
  const [filter, setFilter] = useState('All');

  // Pure-visual filter — "Unread" hides papers flagged read; named chips hide
  // anything missing the category. Matches the static mock's behavior.
  const filtered = readingList.filter((p) => {
    if (filter === 'All') return true;
    if (filter === 'Unread') return !p.read;
    return p.categories.includes(filter);
  });

  return (
    <div>
      <h2 className="sr-only">
        Paper Aggregator — reading list and daily feed digest video
      </h2>

      <PageTabs tabs={PAGE_TABS} active={pageTab} onChange={setPageTab} />

      <div className={styles.body}>
        <div>
          {/* READING LIST CARD ------------------------------------------- */}
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.cardTitle}>
                Reading List · {readingList.length} papers
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

            {filtered.map((paper, i) => (
              <ReadingListRow key={paper.id} paper={paper} index={i} />
            ))}
          </div>

          {/* DIGEST VIDEO CARD ------------------------------------------- */}
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.cardTitle}>▶ Today's Feed — Digest Video</div>
              <button type="button" className={styles.cardAction}>
                Download
              </button>
            </div>
            <div className={styles.genDone}>
              <div className={styles.genDot} />
              Digest video generated · Apr 23, 2026 at 6:30 AM · 12 papers · 18 min 40 sec
            </div>

            <DigestVideo
              chapters={chapters}
              slides={slides}
              totalSeconds={TOTAL_SECONDS}
            />

            <div className={styles.actionRow}>
              <button type="button" className={styles.actionBtn}>
                Re-generate digest
              </button>
              <button type="button" className={styles.actionBtn}>
                Download video
              </button>
              <button type="button" className={styles.actionBtn}>
                Email to me
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT SIDEBAR ------------------------------------------------- */}
        <aside>
          <Widget title="Reading List Stats">
            {stats.map((row) => (
              <div key={row.label} className={widgetStyles.statRow}>
                <span className={widgetStyles.statLabel}>{row.label}</span>
                <span className={widgetStyles.statVal}>{row.value}</span>
              </div>
            ))}
          </Widget>

          <Widget title="Categories">
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
                  <span
                    style={{ fontSize: 12, color: 'var(--color-text-tertiary)' }}
                  >
                    {c.count} paper{c.count === 1 ? '' : 's'}
                  </span>
                </div>
              ))}
            </div>
          </Widget>

          <Widget title="Digest Video">
            <div
              className={styles.genDone}
              style={{ fontSize: 11, marginBottom: 10 }}
            >
              <div className={styles.genDot} />
              Generated today · 18 min 40 sec
            </div>
            <div
              style={{
                fontSize: 11,
                color: 'var(--color-text-tertiary)',
                lineHeight: 1.7,
                marginBottom: 10,
              }}
            >
              Covers all 12 papers from today's feed with visual summaries, key stats,
              and topic clusters.
            </div>
            <button
              type="button"
              className={styles.actionBtn}
              style={{ width: '100%', justifyContent: 'center', fontSize: 12 }}
            >
              ▶ Watch digest
            </button>
          </Widget>
        </aside>
      </div>

      {/* Visual-only tab state; the digest video card always renders in this
          port. Hook up routing/conditional rendering if you split them later. */}
      {pageTab === '__unused__' ? null : null}
    </div>
  );
}
