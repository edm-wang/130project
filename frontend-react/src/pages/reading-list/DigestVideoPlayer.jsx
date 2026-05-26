import { formatClock } from '../../lib/format.js';
import IntroSlide from './slides/IntroSlide.jsx';
import PaperSlide, {
  BarChartBody,
  InsightBody,
  StatStripBody,
} from './slides/PaperSlide.jsx';
import SummarySlide from './slides/SummarySlide.jsx';
import ThemeClustersSlide from './slides/ThemeClustersSlide.jsx';
import styles from './DigestVideoPlayer.module.css';

const SPEEDS = [1, 1.5, 2];

function chapterFor(elapsed, chapters) {
  let idx = 0;
  chapters.forEach((c, i) => {
    if (elapsed >= c.start) idx = i;
  });
  return idx;
}

/**
 * Controlled player. Playback state lives in <DigestVideo /> so the
 * chapter list and the player advance together.
 *
 * Behavior ported from the inline <script> in frontend/reading_list.html.
 */
export default function DigestVideoPlayer({
  chapters,
  slides,
  totalSeconds,
  elapsed,
  playing,
  speed,
  onSeek,
  onTogglePlay,
  onSpeedChange,
}) {
  const currentChapterIdx = chapterFor(elapsed, chapters);
  const currentSlideIdx = chapters[currentChapterIdx].slide;

  const onTrackClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const ratio = (e.clientX - rect.left) / rect.width;
    onSeek(Math.max(0, Math.min(1, ratio)) * totalSeconds);
  };

  return (
    <div className={styles.shell}>
      <div className={styles.screen}>
        {slides.map((slide, i) => {
          const active = i === currentSlideIdx;
          if (slide.kind === 'intro') return <IntroSlide key={i} active={active} />;
          if (slide.kind === 'themes')
            return <ThemeClustersSlide key={i} active={active} />;
          if (slide.kind === 'summary')
            return <SummarySlide key={i} active={active} />;
          const variantIndex = i - 1; // slides 1..3 map to s1..s3 backgrounds
          let body = null;
          if (slide.body && slide.body.type === 'insight')
            body = <InsightBody text={slide.body.text} />;
          else if (slide.body && slide.body.type === 'bars')
            body = (
              <BarChartBody bars={slide.body.bars} caption={slide.body.caption} />
            );
          else if (slide.body && slide.body.type === 'stats')
            body = <StatStripBody stats={slide.body.stats} />;
          return (
            <PaperSlide
              key={i}
              active={active}
              variantIndex={variantIndex}
              label={slide.label}
              title={slide.title}
              authors={slide.authors}
            >
              {body}
            </PaperSlide>
          );
        })}
      </div>

      <div className={styles.controls}>
        <div className={styles.progRow}>
          <span className={styles.time}>{formatClock(elapsed)}</span>
          <div className={styles.track} onClick={onTrackClick}>
            <div
              className={styles.fill}
              style={{ width: `${(elapsed / totalSeconds) * 100}%` }}
            />
          </div>
          <span className={styles.time} style={{ textAlign: 'right' }}>
            {formatClock(totalSeconds)}
          </span>
        </div>
        <div className={styles.ctrlRow}>
          <button type="button" className={styles.playBtn} onClick={onTogglePlay}>
            {playing ? (
              <div className={styles.pauseIcon}>
                <div className={styles.pauseBar} />
                <div className={styles.pauseBar} />
              </div>
            ) : (
              <div className={styles.playIcon} />
            )}
          </button>
          <span className={styles.chLabel}>{chapters[currentChapterIdx].label}</span>
          {SPEEDS.map((s) => (
            <button
              key={s}
              type="button"
              className={[styles.spd, speed === s ? styles.selected : '']
                .join(' ')
                .trim()}
              onClick={() => onSpeedChange(s)}
            >
              {s}×
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
