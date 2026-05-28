import styles from './VideoSummaryPlayer.module.css';

/**
 * The paper-detail page's video summary is currently a static thumbnail
 * with a play button. Mirrors the structure of DigestVideoPlayer but
 * without playback logic.
 */
export default function VideoSummaryPlayer({ video, paper }) {
  return (
    <div className={styles.shell}>
      <div className={styles.bg}>
        <div className={styles.bar} />
        <div className={styles.titleOverlay}>{paper.title}</div>
        <div className={styles.subOverlay}>{paper.affiliation.toUpperCase()}</div>
        <div style={{ height: 16 }} />
        <button type="button" className={styles.playBtn}>
          <div className={styles.playIcon} />
        </button>
      </div>
      <div className={styles.progressBar}>
        <div className={styles.track}>
          <div
            className={styles.fill}
            style={{ width: `${Math.round(video.progress * 100)}%` }}
          />
        </div>
        <div className={styles.controls}>
          <span className={styles.time}>{video.currentLabel}</span>
          <div className={styles.actions}>
            <button type="button" className={styles.ctrlBtn}>
              0.5×
            </button>
            <button type="button" className={styles.ctrlBtn}>
              1×
            </button>
            <button type="button" className={styles.ctrlBtn}>
              1.5×
            </button>
            <button type="button" className={styles.ctrlBtn}>
              ⛶
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
