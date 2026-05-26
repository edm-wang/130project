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
