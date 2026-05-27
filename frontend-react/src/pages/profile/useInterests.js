// [GenAI Usage] Prompt:
// Create a useInterests React hook that fetches GET /users/me/interests and exposes add() and
// remove() functions. add() calls POST /users/me/interests and appends the returned row to local
// state; remove() calls DELETE and filters the row out. In mock mode, flatten the grouped
// interests mockData object into a flat array and simulate add/remove locally. This hook is
// shared by both ProfilePage and FeedPage.
// [GenAI Usage] Response Starts:
import { useCallback, useEffect, useState } from 'react';

import useAuth from '../../hooks/useAuth.js';
import {
  addInterest as addInterestApi,
  deleteInterest,
  fetchInterests,
  isMockMode,
} from '../../lib/api.js';
import { interests as mockInterests } from './mockData.js';

function flattenMockInterests() {
  const flat = [];
  let idx = 0;
  for (const [type, values] of Object.entries(mockInterests)) {
    for (const value of values) {
      flat.push({ id: `mock-${type}-${idx++}`, interest_type: type, value, preference_weight: 1.0 });
    }
  }
  return flat;
}

export default function useInterests() {
  const auth = useAuth();
  const accessToken = auth.session ? auth.session.access_token : '';

  const [state, setState] = useState({ status: 'loading', interests: [], error: '' });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (isMockMode()) {
        if (!cancelled) setState({ status: 'ready', interests: flattenMockInterests(), error: '' });
        return;
      }

      if (auth.status === 'loading') {
        if (!cancelled) setState((s) => ({ ...s, status: 'loading' }));
        return;
      }

      if (auth.status === 'signed-out' || auth.status === 'unconfigured') {
        if (!cancelled) setState({ status: 'no-token', interests: [], error: '' });
        return;
      }

      if (!cancelled) setState((s) => ({ ...s, status: 'loading' }));

      try {
        const data = await fetchInterests();
        if (cancelled) return;
        setState({
          status: 'ready',
          interests: Array.isArray(data.interests) ? data.interests : [],
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
          interests: [],
          error: (err && err.message) || 'Unknown error',
        });
      }
    }

    load();
    return () => { cancelled = true; };
  }, [auth.status, accessToken]); // eslint-disable-line react-hooks/exhaustive-deps

  const add = useCallback(async (value, interest_type) => {
    if (isMockMode()) {
      const newInterest = { id: `mock-${Date.now()}`, interest_type, value, preference_weight: 1.0 };
      setState((s) => ({ ...s, interests: [...s.interests, newInterest] }));
      return newInterest;
    }
    const newInterest = await addInterestApi(value, interest_type);
    setState((s) => ({
      ...s,
      interests: [...s.interests.filter((i) => i.id !== newInterest.id), newInterest],
    }));
    return newInterest;
  }, []);

  const remove = useCallback(async (interestId) => {
    if (isMockMode()) {
      setState((s) => ({ ...s, interests: s.interests.filter((i) => i.id !== interestId) }));
      return;
    }
    await deleteInterest(interestId);
    setState((s) => ({ ...s, interests: s.interests.filter((i) => i.id !== interestId) }));
  }, []);

  return { ...state, add, remove };
}
// [GenAI Usage] Response Ends
// [GenAI Usage] Reflection:
// I used Claude Code for this hook because it is structurally identical to useProfile — same
// auth gating and cancellation pattern. I reviewed the upsert behaviour for add(): filtering
// the returned row by id before appending handles the case where a soft-deleted interest is
// re-added (the backend upserts and returns the existing row with a different id than any
// optimistic placeholder). I also confirmed the mock flattenMockInterests() produces the same
// { id, interest_type, value } shape that InterestSection and FeedPage's InterestTag expect.
