import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import ChapterList from './ChapterList.jsx';
import PaperHeader from './PaperHeader.jsx';
import {
  RelatedPapersCard,
  SavedToReadingListCard,
  ShareCard,
  VideoSidebarCard,
  YourVoteCard,
} from './SidebarCards.jsx';
import SummaryTabs from './SummaryTabs.jsx';
import TextSummary from './TextSummary.jsx';
import VideoSummaryPlayer from './VideoSummaryPlayer.jsx';
import { getPaperDetail } from './mockData.js';
import styles from './PaperDetailPage.module.css';

export default function PaperDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const paper = getPaperDetail(id);
  const [tab, setTab] = useState('text');

  return (
    <div>
      <h2 className="sr-only">
        Paper Aggregator — paper detail with text and video summary
      </h2>

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

      <div className={styles.body}>
        <div>
          <PaperHeader paper={paper} />

          <div className={styles.card}>
            <SummaryTabs active={tab} onChange={setTab} />

            {tab === 'text' ? <TextSummary summary={paper.summary} /> : null}

            {tab === 'video' ? (
              <div>
                <div className={styles.genStatus}>
                  <div className={styles.genDot} />
                  Video generated · {paper.video.generatedAt} · {paper.video.lengthLabel}
                </div>
                <VideoSummaryPlayer video={paper.video} paper={paper} />
                <div className={styles.sectionLabel} style={{ marginBottom: 8 }}>
                  Chapters
                </div>
                <ChapterList chapters={paper.video.chapters} />
              </div>
            ) : null}

            {tab === 'abstract' ? (
              <div
                style={{
                  fontSize: 13,
                  color: 'var(--color-text-secondary)',
                  lineHeight: 1.8,
                }}
              >
                Abstract content not available in this mock.
              </div>
            ) : null}
          </div>

          {/* Standalone video card matches the original mock layout where the
              video lives below the text summary card. */}
          <div className={styles.card}>
            <div className={styles.sectionLabel}>▶ Video Summary</div>
            <div className={styles.genStatus}>
              <div className={styles.genDot} />
              Video generated · {paper.video.generatedAt} · {paper.video.lengthLabel}
            </div>
            <VideoSummaryPlayer video={paper.video} paper={paper} />
            <div className={styles.sectionLabel} style={{ marginBottom: 8 }}>
              Chapters
            </div>
            <ChapterList chapters={paper.video.chapters} />
            <div className={styles.actionRow}>
              <button type="button" className={styles.actionBtn}>
                Re-generate video
              </button>
              <button type="button" className={styles.actionBtn}>
                Download video
              </button>
            </div>
          </div>
        </div>

        <aside>
          <SavedToReadingListCard paper={paper} />
          <YourVoteCard paper={paper} />
          <VideoSidebarCard video={paper.video} />
          <ShareCard />
          <RelatedPapersCard related={paper.related} />
        </aside>
      </div>
    </div>
  );
}
