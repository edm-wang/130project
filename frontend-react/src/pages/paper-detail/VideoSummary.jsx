// [GenAI Usage] Prompt:
// Create a VideoSummary component that accepts a videoSummary object (from POST
// /papers/:id/video-summary) and an optional onRegenerate callback. Render an HTML5
// <video> with the video_path as src, attach subtitle_vtt_path as a <track> if present,
// show a green "AI video generated" status pill with the slide count, and add a footer
// row with a PPTX download link and a Regenerate button. Mirror the visual style of
// TextSummary (genStatus/genDot/footerRow pattern).
// [GenAI Usage] Response begins:
// [GenAI Usage 2] Prompt: Extend VideoSummary with chapter navigation driven by the
// script array (start_seconds, end_seconds, slide_title). Add a timeupdate listener
// that highlights the active chapter by walking the script in reverse. Render a
// proportional timeline bar (segment width = chapter duration / total) and a chapter
// list with timestamp + title, both clickable to seek. Style active chapter with brand
// color consistent with the app's design tokens.
// [GenAI Usage 2] Response begins:
import { useEffect, useRef, useState } from 'react';

import PillButton from '../../components/atoms/PillButton.jsx';
import styles from './VideoSummary.module.css';

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}

export default function VideoSummary({ videoSummary, onRegenerate }) {
  const videoRef = useRef(null);
  const [activeChapter, setActiveChapter] = useState(0);

  const script = videoSummary.script || [];
  const totalDuration = script.length > 0 ? script[script.length - 1].end_seconds : 0;

  useEffect(() => {
    const video = videoRef.current;
    if (!video || script.length === 0) return;
    function handleTimeUpdate() {
      const t = video.currentTime;
      for (let i = script.length - 1; i >= 0; i--) {
        if (t >= script[i].start_seconds) {
          setActiveChapter(i);
          return;
        }
      }
      setActiveChapter(0);
    }
    video.addEventListener('timeupdate', handleTimeUpdate);
    return () => video.removeEventListener('timeupdate', handleTimeUpdate);
  }, [script]);

  function seekTo(seconds) {
    if (videoRef.current) {
      videoRef.current.currentTime = seconds;
      videoRef.current.play();
    }
  }
  // [GenAI Usage 2] Response ends
  // [GenAI Usage 2] Reflection: The timeupdate handler walks the script in reverse so it
  // finds the correct chapter in one pass without needing a binary search — n is at most 8
  // slides so this is fine. The effect depends only on `script` (not `activeChapter`) to
  // avoid re-registering the listener on every highlight change. Segment widths are computed
  // as percentages of totalDuration so the timeline scales correctly regardless of slide count.

  return (
    <div>
      <div className={styles.genStatus}>
        <div className={styles.genDot} />
        AI video generated · {script.length} slides
      </div>

      <video ref={videoRef} className={styles.player} controls src={videoSummary.video_path}>
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

      {script.length > 0 && (
        <>
          {/* [GenAI Usage 2] Response begins: */}
          <div className={styles.timeline}>
            {script.map((ch, i) => (
              <button
                key={i}
                type="button"
                className={[styles.timelineSegment, i === activeChapter ? styles.timelineActive : ''].join(' ').trim()}
                style={{ width: `${((ch.end_seconds - ch.start_seconds) / totalDuration) * 100}%` }}
                onClick={() => seekTo(ch.start_seconds)}
                title={ch.slide_title}
              />
            ))}
          </div>

          <div className={styles.chapters}>
            {script.map((ch, i) => (
              <button
                key={i}
                type="button"
                className={[styles.chapter, i === activeChapter ? styles.chapterActive : ''].join(' ').trim()}
                onClick={() => seekTo(ch.start_seconds)}
              >
                <span className={styles.chapterTime}>{formatTime(ch.start_seconds)}</span>
                <span className={styles.chapterTitle}>{ch.slide_title}</span>
              </button>
            ))}
          </div>
          {/* [GenAI Usage 2] Response ends */}
        </>
      )}

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
// The chapter/timeline feature walks the script array in reverse on each timeupdate event
// to find the active chapter in O(n) without needing sorted search, since n is small (≤8).
