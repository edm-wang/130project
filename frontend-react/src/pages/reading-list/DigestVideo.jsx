import { useEffect, useRef, useState } from 'react';

import DigestChapterList from './DigestChapterList.jsx';
import DigestVideoPlayer from './DigestVideoPlayer.jsx';

/**
 * Holds the shared playback state so the player and the chapter list both
 * advance together. Equivalent to the global `elapsed/playing/spd` variables
 * in the original inline script.
 */
function chapterFor(elapsed, chapters) {
  let idx = 0;
  chapters.forEach((c, i) => {
    if (elapsed >= c.start) idx = i;
  });
  return idx;
}

export default function DigestVideo({ chapters, slides, totalSeconds }) {
  const [elapsed, setElapsed] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);

  const rafRef = useRef(null);
  const lastTsRef = useRef(null);

  useEffect(() => {
    if (!playing) return undefined;
    const tick = (ts) => {
      if (lastTsRef.current == null) lastTsRef.current = ts;
      const delta = ((ts - lastTsRef.current) / 1000) * speed;
      lastTsRef.current = ts;
      setElapsed((prev) => {
        const next = Math.min(prev + delta, totalSeconds);
        if (next >= totalSeconds) setPlaying(false);
        return next;
      });
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      lastTsRef.current = null;
    };
  }, [playing, speed, totalSeconds]);

  const activeChapter = chapterFor(elapsed, chapters);

  return (
    <>
      <DigestVideoPlayer
        chapters={chapters}
        slides={slides}
        totalSeconds={totalSeconds}
        elapsed={elapsed}
        playing={playing}
        speed={speed}
        onSeek={(v) => {
          lastTsRef.current = null;
          setElapsed(v);
        }}
        onTogglePlay={() => {
          if (elapsed >= totalSeconds) setElapsed(0);
          lastTsRef.current = null;
          setPlaying((p) => !p);
        }}
        onSpeedChange={setSpeed}
      />
      <DigestChapterList
        chapters={chapters}
        activeIndex={activeChapter}
        onJump={(i) => {
          setElapsed(chapters[i].start);
          lastTsRef.current = null;
        }}
      />
    </>
  );
}
