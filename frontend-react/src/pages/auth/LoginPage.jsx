import { useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';

import useAuth from '../../hooks/useAuth.js';
import { hasSupabaseConfig, supabase } from '../../lib/supabase.js';
import styles from './LoginPage.module.css';

const TABS = [
  { id: 'sign-in', label: 'Sign in' },
  { id: 'sign-up', label: 'Sign up' },
];

export default function LoginPage() {
  const auth = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const [tab, setTab] = useState('sign-in');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');

  if (auth.status === 'signed-in') {
    // Honor a ?next= redirect from RequireAuth, otherwise send to /feed.
    const next = new URLSearchParams(location.search).get('next') || '/feed';
    return <Navigate to={next} replace />;
  }

  const submit = async (e) => {
    e.preventDefault();
    if (!hasSupabaseConfig) return;
    setError('');
    setInfo('');
    setBusy(true);
    try {
      if (tab === 'sign-in') {
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        });
        if (signInError) throw signInError;
        const next = new URLSearchParams(location.search).get('next') || '/feed';
        navigate(next, { replace: true });
      } else {
        const { error: signUpError } = await supabase.auth.signUp({
          email: email.trim(),
          password,
        });
        if (signUpError) throw signUpError;
        setInfo(
          'Account created. Check your email for a confirmation link before signing in.',
        );
      }
    } catch (err) {
      setError((err && err.message) || 'Unknown error');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className={styles.wrap}>
      <div className={styles.card}>
        <div className={styles.title}>
          Paper<span style={{ color: 'var(--color-brand)' }}>Agg</span>
        </div>
        <div className={styles.sub}>
          Sign in to see your personalized feed.
        </div>

        {!hasSupabaseConfig ? (
          <div className={styles.notice}>
            Supabase env vars are not set. Add{' '}
            <code>VITE_SUPABASE_URL</code> and{' '}
            <code>VITE_SUPABASE_PUBLISHABLE_KEY</code> to{' '}
            <code>.env.development</code> and restart <code>npm run dev</code>.
            Until then the app cannot authenticate.
          </div>
        ) : null}

        <div className={styles.tabs}>
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              className={[styles.tab, tab === t.id ? styles.active : '']
                .join(' ')
                .trim()}
              onClick={() => {
                setTab(t.id);
                setError('');
                setInfo('');
              }}
            >
              {t.label}
            </button>
          ))}
        </div>

        {error ? <div className={styles.error}>{error}</div> : null}
        {info ? <div className={styles.success}>{info}</div> : null}

        <form onSubmit={submit}>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="email">
              Email
            </label>
            <input
              id="email"
              className={styles.input}
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="password">
              Password
            </label>
            <input
              id="password"
              className={styles.input}
              type="password"
              autoComplete={
                tab === 'sign-in' ? 'current-password' : 'new-password'
              }
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button
            type="submit"
            className={styles.submit}
            disabled={busy || !hasSupabaseConfig}
          >
            {busy
              ? '…'
              : tab === 'sign-in'
                ? 'Sign in'
                : 'Create account'}
          </button>
        </form>
      </div>
    </div>
  );
}
