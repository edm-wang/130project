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
