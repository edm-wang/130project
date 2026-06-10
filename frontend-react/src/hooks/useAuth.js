// [GenAI Usage] Prompt: I need a hook that other components (RequireAuth, Navbar, LoginPage,
// useRecommendations) can all call to find out whether someone is signed in, get their session/
// access token, and sign out. It needs to handle the case where Supabase env vars aren't set at
// all (so the demo doesn't just crash), check for an existing session on load, and keep itself
// up to date if the user logs in/out or their token refreshes in another tab or component.
// [GenAI Usage] Response Starts:
import { useEffect, useState } from 'react';

import { hasSupabaseConfig, supabase } from '../lib/supabase.js';

/**
 * Returns the current Supabase session, user, and a sign-out helper.
 *
 * `status` is one of:
 *   - 'unconfigured' — VITE_SUPABASE_* env vars aren't set
 *   - 'loading'      — initial getSession() hasn't resolved yet
 *   - 'signed-in'    — there's an active session
 *   - 'signed-out'   — no session
 *
 * Subscribes to onAuthStateChange so the UI updates on login / logout /
 * token refresh from anywhere in the app.
 */
export default function useAuth() {
  const [state, setState] = useState({
    status: hasSupabaseConfig ? 'loading' : 'unconfigured',
    session: null,
    user: null,
  });

  useEffect(() => {
    if (!hasSupabaseConfig) return undefined;

    let cancelled = false;

    supabase.auth.getSession().then(({ data }) => {
      if (cancelled) return;
      setState({
        status: data.session ? 'signed-in' : 'signed-out',
        session: data.session,
        user: data.session ? data.session.user : null,
      });
    });

    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      setState({
        status: session ? 'signed-in' : 'signed-out',
        session,
        user: session ? session.user : null,
      });
    });

    return () => {
      cancelled = true;
      sub.subscription.unsubscribe();
    };
  }, []);

  const signOut = async () => {
    if (!hasSupabaseConfig) return;
    await supabase.auth.signOut();
  };

  return { ...state, signOut };
}
// [GenAI Usage] Response Ends
// [GenAI Reflection] I had Claude Code write this because the cancelled-flag pattern in the
// useEffect (to avoid setting state after unmount) and unsubscribing from
// onAuthStateChange in the cleanup function are things I'd have gotten wrong on my own.
// I originally forgot the unsubscribe entirely and React was warning about state updates on an
// unmounted component during fast page switches. The four-state status enum
// (unconfigured/loading/signed-in/signed-out) was my idea since RequireAuth and LoginPage both
// need to branch on it, but I asked the LLM to make sure every code path actually sets one of
// those four values so nothing falls through to undefined.
