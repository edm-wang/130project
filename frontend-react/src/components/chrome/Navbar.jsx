import { NavLink, useNavigate } from 'react-router-dom';

import useAuth from '../../hooks/useAuth.js';
import Avatar from '../atoms/Avatar.jsx';
import SearchBar from '../atoms/SearchBar.jsx';
import styles from './Navbar.module.css';

const LINKS = [
  { to: '/feed', label: 'Feed' },
  { to: '/reading-list', label: 'Reading List' },
];

function deriveInitials(email) {
  if (!email) return '·';
  const local = email.split('@')[0] || '';
  const parts = local.split(/[.\-_]+/).filter(Boolean);
  if (parts.length === 0) return local.slice(0, 2).toUpperCase();
  return (parts[0][0] + (parts[1] ? parts[1][0] : '')).toUpperCase();
}

export default function Navbar() {
  const navigate = useNavigate();
  const { status, user, signOut } = useAuth();

  const initials = deriveInitials(user && user.email);
  const displayName = user ? user.email : 'Not signed in';

  // [GenAI Usage] Prompt: Integrate the SearchBar component into the navbar between the
  // navigation links and the user profile section. The search handler should pass the query
  // to the feed page via React Router state so the feed can filter papers client-side. I
  // chose to use navigation state instead of URL params to keep the URL clean and because
  // the search is temporary/ephemeral rather than something users would bookmark.
  // [GenAI Usage] LLM response begins:
  const handleSearch = (query) => {
    console.log('Search query:', query);
    navigate('/feed', { state: { searchQuery: query } });
  };
  // [GenAI Usage] LLM response ends

  return (
    <nav className={styles.nav}>
      <button
        type="button"
        onClick={() => navigate('/feed')}
        className={styles.logo}
        style={{ border: 'none', background: 'none', padding: 0 }}
      >
        Paper<span>Agg</span>
      </button>

      <div className={styles.navLinks}>
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              [styles.navLink, isActive ? styles.active : ''].join(' ').trim()
            }
            end={link.to === '/feed'}
          >
            {link.label}
          </NavLink>
        ))}
      </div>

      <SearchBar onSearch={handleSearch} placeholder="Search papers..." />

      <div className={styles.userBlock}>
        {status === 'signed-in' ? (
          <>
            <span className={styles.userName}>{displayName}</span>
            <button
              type="button"
              onClick={() => navigate('/profile')}
              style={{ background: 'none', border: 'none', padding: 0, cursor: 'pointer' }}
              aria-label="Go to profile"
            >
              <Avatar initials={initials} />
            </button>
            <button
              type="button"
              onClick={async () => {
                await signOut();
                navigate('/auth/login');
              }}
              style={{
                fontSize: 12,
                padding: '4px 10px',
                border: '0.5px solid var(--color-border-tertiary)',
                borderRadius: 'var(--border-radius-md)',
                background: 'none',
                color: 'var(--color-text-secondary)',
              }}
            >
              Sign out
            </button>
          </>
        ) : status === 'unconfigured' ? (
          <span className={styles.userName} title="Set VITE_SUPABASE_* env vars">
            Demo mode
          </span>
        ) : status === 'loading' ? (
          <span className={styles.userName}>…</span>
        ) : (
          <button
            type="button"
            onClick={() => navigate('/auth/login')}
            style={{
              fontSize: 12,
              padding: '4px 10px',
              border: '0.5px solid var(--color-border-tertiary)',
              borderRadius: 'var(--border-radius-md)',
              background: 'none',
              color: 'var(--color-text-secondary)',
            }}
          >
            Sign in
          </button>
        )}
      </div>
    </nav>
  );
}
