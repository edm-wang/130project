// [GenAI Usage] Prompt:
// Create a useSavedPapers React hook that fetches GET /saved-papers and maps the API response
// to the shape ReadingListRow expects (id, title, meta string from authors+year, categories array,
// isNew flag from created_at). It should also derive filterChips from the actual paper categories
// and support VITE_USE_MOCK_DATA mode by returning the existing readingList mock.
// [GenAI Usage] Response Starts:
import { useEffect, useState } from 'react';

import useAuth from '../../hooks/useAuth.js';
import { fetchSavedPapers, isMockMode } from '../../lib/api.js';
import { readingList as mockReadingList } from './mockData.js';

function formatMeta(authorsText, publishedAt) {
  const authorPart = authorsText || 'Unknown authors';
  const yearPart = publishedAt ? ` · ${new Date(publishedAt).getFullYear()}` : '';
  return `${authorPart}${yearPart}`;
}

function toRowShape(row) {
  const paper = row.paper || {};
  const isNew = Date.now() - new Date(row.created_at).getTime() < 48 * 60 * 60 * 1000;
  return {
    id: row.paper_id,
    title: paper.title || '(untitled)',
    meta: formatMeta(paper.authors_text, paper.published_at),
    categories: Array.isArray(paper.categories) ? paper.categories : [],
    isNew,
    read: false,
    sourceUrl: paper.source_url || null,
  };
}

function deriveChips(papers) {
  const categories = [...new Set(papers.flatMap((p) => p.categories))];
  return ['All', ...categories, 'Unread'];
}

export default function useSavedPapers() {
  const auth = useAuth();
  const accessToken = auth.session ? auth.session.access_token : '';

  const [state, setState] = useState({
    status: 'loading',
    savedPapers: [],
    filterChips: ['All', 'Unread'],
    error: '',
  });

  function removePaper(paperId) {
    setState((s) => {
      const updated = s.savedPapers.filter((p) => p.id !== paperId);
      return { ...s, savedPapers: updated, filterChips: deriveChips(updated) };
    });
  }

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (isMockMode()) {
        if (!cancelled)
          setState({
            status: 'ready',
            savedPapers: mockReadingList,
            filterChips: deriveChips(mockReadingList),
            error: '',
          });
        return;
      }

      if (auth.status === 'loading') {
        if (!cancelled) setState((s) => ({ ...s, status: 'loading' }));
        return;
      }

      if (auth.status === 'signed-out' || auth.status === 'unconfigured') {
        if (!cancelled)
          setState({
            status: 'no-token',
            savedPapers: [],
            filterChips: ['All', 'Unread'],
            error: 'Sign in to see your reading list.',
          });
        return;
      }

      if (!cancelled) setState((s) => ({ ...s, status: 'loading' }));

      try {
        const data = await fetchSavedPapers();
        if (cancelled) return;
        const papers = (data.saved_papers || []).filter((r) => r.paper).map(toRowShape);
        setState({
          status: 'ready',
          savedPapers: papers,
          filterChips: deriveChips(papers),
          error: '',
        });
      } catch (err) {
        if (cancelled) return;
        const code = err && err.code;
        setState({
          status:
            code === 'NO_TOKEN' ? 'no-token'
            : code === 'NETWORK' ? 'network-error'
            : code === 'UNAUTHORIZED' ? 'unauthorized'
            : 'error',
          savedPapers: [],
          filterChips: ['All', 'Unread'],
          error: (err && err.message) || 'Unknown error',
        });
      }
    }

    load();
    return () => { cancelled = true; };
  }, [auth.status, accessToken]); // eslint-disable-line react-hooks/exhaustive-deps

  return { ...state, removePaper };
}
// [GenAI Usage] Response Ends
// [GenAI Usage] Reflection:
// I used Claude Code for this hook because the data transformation (API row → ReadingListRow shape)
// is mechanical but easy to get wrong. I reviewed the toRowShape mapping carefully: confirmed
// paper_id (not saved_papers.id) is used as the row key since ReadingListRow navigates to
// /papers/{id}, checked the meta formatter handles null authors_text and null published_at without
// crashing, and verified the 48-hour isNew window uses Date.now() correctly. I also confirmed
// that rows with a null paper join are filtered out to guard against orphaned saved_papers rows.
// Later added removePaper so the reading list page can do an optimistic delete: the function
// filters the paper out of savedPapers and re-derives filterChips in one setState call, keeping
// the chip counts in sync without needing a full refetch after the DELETE /saved-papers/:id call.
