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
