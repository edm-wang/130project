/** Format an ISO date as e.g. "Apr 23". Returns '' on missing/invalid input. */
export function formatShortDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? ''
    : d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

/** Format an ISO date as e.g. "Thursday, April 23". Returns '' on missing/invalid input. */
export function formatLongDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? ''
    : d.toLocaleDateString(undefined, {
        weekday: 'long',
        month: 'long',
        day: 'numeric',
      });
}

/** Format a number of seconds as "M:SS". */
export function formatClock(secs) {
  const s = Math.max(0, Math.floor(secs));
  const m = Math.floor(s / 60);
  return `${m}:${String(s % 60).padStart(2, '0')}`;
}
