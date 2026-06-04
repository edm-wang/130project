// [GenAI Usage] Prompt:
// Create a VideoSummary component that accepts a videoSummary object (from POST
// /papers/:id/video-summary) and an optional onRegenerate callback. Render an HTML5
// <video> with the video_path as src, attach subtitle_vtt_path as a <track> if present,
// show a green "AI video generated" status pill with the slide count, and add a footer
// row with a PPTX download link and a Regenerate button. Mirror the visual style of
// TextSummary (genStatus/genDot/footerRow pattern).
// [GenAI Usage] Response begins:
import PillButton from '../../components/atoms/PillButton.jsx';
import styles from './VideoSummary.module.css';

export default function VideoSummary({ videoSummary, onRegenerate }) {
  return (
    <div>
      <div className={styles.genStatus}>
        <div className={styles.genDot} />
        AI video generated · {videoSummary.slides?.length ?? 0} slides
      </div>
      <video className={styles.player} controls src={videoSummary.video_path}>
        {videoSummary.subtitle_vtt_path && (
          <track
            kind="subtitles"
            src={videoSummary.subtitle_vtt_path}
            srcLang="en"
            label="English"
            default
          />
        )}
      </video>
      <div className={styles.footerRow}>
        {videoSummary.pptx_path && (
          <a
            className={styles.downloadLink}
            href={videoSummary.pptx_path}
            target="_blank"
            rel="noreferrer"
          >
            ↓ Download slides (.pptx)
          </a>
        )}
        {onRegenerate && (
          <PillButton style={{ fontSize: 11 }} onClick={onRegenerate}>
            Regenerate video
          </PillButton>
        )}
      </div>
    </div>
  );
}
// [GenAI Usage] Response ends
// [GenAI Reflection] I used Claude Code to scaffold this component because the structure
// closely parallels TextSummary (status pill + main content + footer row) but swaps the
// ReactMarkdown block for an HTML5 video element with a VTT subtitle track. The key detail
// is that video_path and subtitle_vtt_path are durable Supabase Storage public URLs, so
// no auth header is needed — they can be used directly as <video src> and <track src>.
