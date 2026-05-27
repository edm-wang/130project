// [GenAI Usage] Prompt:
// Create a useProfile React hook following the useRecommendations.js pattern. It should fetch
// GET /users/me, handle the null-profile case (no app_users row yet) with a 'no-profile' status
// for the frontend to show a "complete your profile" prompt, expose a save() function that calls
// PUT /users/me and updates local state, and support VITE_USE_MOCK_DATA mode.
// [GenAI Usage] Response Starts:
import { useCallback, useEffect, useState } from 'react';

import useAuth from '../../hooks/useAuth.js';
import { fetchProfile, isMockMode, saveProfile as saveProfileApi } from '../../lib/api.js';
import { editFields, profile as mockProfile } from './mockData.js';

const MOCK_PROFILE = {
  display_name: editFields.displayName,
  institution: editFields.affiliation,
  bio: editFields.bio,
  email: editFields.email,
};

export default function useProfile() {
  const auth = useAuth();
  const accessToken = auth.session ? auth.session.access_token : '';

  const [state, setState] = useState({ status: 'loading', profile: null, error: '' });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (isMockMode()) {
        if (!cancelled) setState({ status: 'ready', profile: MOCK_PROFILE, error: '' });
        return;
      }

      if (auth.status === 'loading') {
        if (!cancelled) setState((s) => ({ ...s, status: 'loading' }));
        return;
      }

      if (auth.status === 'signed-out' || auth.status === 'unconfigured') {
        if (!cancelled)
          setState({ status: 'no-token', profile: null, error: 'Sign in to view your profile.' });
        return;
      }

      if (!cancelled) setState((s) => ({ ...s, status: 'loading' }));

      try {
        const data = await fetchProfile();
        if (cancelled) return;
        setState(
          data.profile
            ? { status: 'ready', profile: data.profile, error: '' }
            : { status: 'no-profile', profile: null, error: '' },
        );
      } catch (err) {
        if (cancelled) return;
        const code = err && err.code;
        setState({
          status:
            code === 'NO_TOKEN' ? 'no-token'
            : code === 'NETWORK' ? 'network-error'
            : code === 'UNAUTHORIZED' ? 'unauthorized'
            : 'error',
          profile: null,
          error: (err && err.message) || 'Unknown error',
        });
      }
    }

    load();
    return () => { cancelled = true; };
  }, [auth.status, accessToken]); // eslint-disable-line react-hooks/exhaustive-deps

  const save = useCallback(async (fields) => {
    if (isMockMode()) {
      setState((s) => ({
        ...s,
        profile: s.profile
          ? { ...s.profile, display_name: fields.displayName, institution: fields.affiliation, bio: fields.bio }
          : { display_name: fields.displayName, institution: fields.affiliation, bio: fields.bio, email: '' },
      }));
      return;
    }
    const data = await saveProfileApi({
      display_name: fields.displayName,
      institution: fields.affiliation,
      bio: fields.bio,
    });
    setState((s) => ({ ...s, status: 'ready', profile: data.profile }));
  }, []); // setState is stable

  return { ...state, save };
}
// [GenAI Usage] Response Ends
// [GenAI Usage] Reflection:
// I used Claude Code here because the hook structure mirrors useRecommendations.js closely —
// same cancellation flag, same auth status gating, same error code mapping. I verified that
// the mock path maps editFields (from mockData) to the same field shape the API returns
// (display_name, institution, bio, email), and confirmed that save() guards against calling
// the API in mock mode so it still gives a working save interaction during development.
