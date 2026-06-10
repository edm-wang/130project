// [GenAI Usage] Prompt: I need a wrapper component that checks the auth status from useAuth and
// only renders its children if the user is actually signed in. If they're signed out, redirect
// to /auth/login but remember where they were trying to go (so after logging in they land back
// on, say, /reading-list instead of always /feed). While the session check is still loading,
// don't redirect yet, just show something minimal so there's no flash of the login page before
// the session loads. If Supabase isn't configured at all, let the page through anyway since I'd
// rather see the page's own error state than a permanent redirect loop.
// [GenAI Usage] Response Starts:
import { Navigate, useLocation } from 'react-router-dom';

import useAuth from '../../hooks/useAuth.js';

/**
 * Route guard. Children render only when the user is signed in.
 *
 * - 'loading'      → tiny placeholder, prevents a flicker to /auth/login
 *                    while getSession() resolves.
 * - 'signed-out'   → redirect to /auth/login?next=<current path>
 * - 'unconfigured' → render children. The page will surface its own state
 *                    when the backend call fails, but we don't block the UI.
 */
export default function RequireAuth({ children }) {
  const auth = useAuth();
  const location = useLocation();

  if (auth.status === 'loading') {
    return (
      <div
        style={{
          padding: '60px 28px',
          textAlign: 'center',
          color: 'var(--color-text-tertiary)',
          fontSize: 13,
        }}
      >
        Checking session…
      </div>
    );
  }

  if (auth.status === 'signed-out') {
    const next = encodeURIComponent(location.pathname + location.search);
    return <Navigate to={`/auth/login?next=${next}`} replace />;
  }

  return children;
}
// [GenAI Usage] Response Ends
// [GenAI Reflection] I used Claude Code mainly to get the "next" redirect param right since I
// kept second-guessing the encodeURIComponent step and whether it should include the query
// string too (it should, otherwise filters/tabs in the URL get dropped after login). The
// 'unconfigured' passthrough was something I added after testing locally without a .env file
// and getting stuck on an infinite redirect to /auth/login, which itself rendered fine but
// looked broken because of the missing-config notice. Letting the page through felt like the
// better failure mode for a demo.
