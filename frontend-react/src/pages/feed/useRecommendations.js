// [GenAI Usage] Prompt: Build the data-fetching hook for FeedPage. It should call
// fetchRecommendations from api.js, but I also want a mock mode (controlled by
// VITE_USE_MOCK_DATA) that returns canned data from mockData.js so I can work on the feed UI
// without the backend running. It needs to track loading/ready/error states, and handle the
// case where the user isn't signed in yet (don't just show a generic error, distinguish
// "no token" from "network error" from "unauthorized" so FeedPage can show different messages).
// Also it should re-fetch automatically if the user's auth state changes, e.g. they sign in
// after landing on the page while signed out.
// [GenAI Usage] Response Starts:
import { useEffect, useState } from 'react';

import useAuth from '../../hooks/useAuth.js';
import { fetchRecommendations, isMockMode } from '../../lib/api.js';
import { mockResponse } from './mockData.js';

/**
 * Hook for the FeedPage. Talks to GET /recommendations or returns mock data
 * when VITE_USE_MOCK_DATA=true.
 *
 * Re-fetches whenever the Supabase access token changes (sign-in / sign-out /
 * token refresh), so the page doesn't show stale data after auth state moves.
 *
 * @returns {{
 *   status: 'idle'|'loading'|'ready'|'error'|'no-token'|'network-error'|'unauthorized',
 *   batch: import('../../shapes/shapes.js').RecommendationBatch | null,
 *   recommendations: import('../../shapes/shapes.js').Recommendation[],
 *   error: string,
 * }}
 */
export default function useRecommendations({ enabled = true } = {}) {
  const auth = useAuth();
  const accessToken = auth.session ? auth.session.access_token : '';

  const [state, setState] = useState({
    status: 'idle',
    batch: null,
    recommendations: [],
    error: '',
  });

  useEffect(() => {
    let cancelled = false;

    if (!enabled) {
      setState({ status: 'idle', batch: null, recommendations: [], error: '' });
      return undefined;
    }

    if (isMockMode()) {
      setState({
        status: 'ready',
        batch: mockResponse.batch,
        recommendations: mockResponse.recommendations,
        error: '',
      });
      return () => {
        cancelled = true;
      };
    }

    // Wait for the auth check before deciding what to do.
    if (auth.status === 'loading') {
      setState((s) => ({ ...s, status: 'loading' }));
      return undefined;
    }

    if (auth.status === 'signed-out' || auth.status === 'unconfigured') {
      setState({
        status: 'no-token',
        batch: null,
        recommendations: [],
        error:
          auth.status === 'unconfigured'
            ? 'Supabase env vars are not configured.'
            : 'Sign in to load your feed.',
      });
      return undefined;
    }

    setState((s) => ({ ...s, status: 'loading' }));
    fetchRecommendations()
      .then((data) => {
        if (cancelled) return;
        setState({
          status: 'ready',
          batch: (data && data.batch) || null,
          recommendations: Array.isArray(data && data.recommendations)
            ? data.recommendations
            : [],
          error: '',
        });
      })
      .catch((err) => {
        if (cancelled) return;
        const code = err && err.code;
        const status =
          code === 'NO_TOKEN'
            ? 'no-token'
            : code === 'NETWORK'
              ? 'network-error'
              : code === 'UNAUTHORIZED'
                ? 'unauthorized'
                : 'error';
        setState({
          status,
          batch: null,
          recommendations: [],
          error: (err && err.message) || 'Unknown error',
        });
      });

    return () => {
      cancelled = true;
    };
    // Re-run when the auth status flips or the access token changes (e.g.
    // refresh). Including the token covers token-refresh edges without
    // forcing the page to remount.
  }, [auth.status, accessToken, enabled]);

  return state;
}
// [GenAI Usage] Response Ends
// [GenAI Reflection] I leaned on Claude Code for the error-code-to-status mapping in the catch
// block (NO_TOKEN/NETWORK/UNAUTHORIZED to 'no-token'/'network-error'/'unauthorized'), since
// those error codes come from apiFetch in api.js and I wanted the mapping to actually line up
// with what that function throws rather than guessing. The mock mode branch was my addition on
// top of the first draft, since I needed to keep building the FeedPage layout while a teammate
// was still finishing the backend recommendations endpoint. I tested both paths by toggling
// VITE_USE_MOCK_DATA in .env.development and confirming the feed renders the same cards either
// way.
