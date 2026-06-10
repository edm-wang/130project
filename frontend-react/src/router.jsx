// [GenAI Usage] Prompt: I'm converting the static pages (index/feed, reading_list, profile_page,
// post_recommendation/paper detail) into routes for a single-page app. I need a router config
// using createBrowserRouter where most pages share a layout with the navbar (AppShell), but
// only render if the user is signed in. The login page should still get the navbar/shell so it
// doesn't look broken, but obviously shouldn't be behind the auth check. Root path "/" should
// just redirect to "/feed".
// [GenAI Usage] Response Starts:
import { createBrowserRouter, Navigate } from 'react-router-dom';

import AppShell from './components/chrome/AppShell.jsx';
import RequireAuth from './components/chrome/RequireAuth.jsx';
import FeedPage from './pages/feed/FeedPage.jsx';
import ReadingListPage from './pages/reading-list/ReadingListPage.jsx';
import ProfilePage from './pages/profile/ProfilePage.jsx';
import PaperDetailPage from './pages/paper-detail/PaperDetailPage.jsx';
import LoginPage from './pages/auth/LoginPage.jsx';

const protectedShell = (
  <RequireAuth>
    <AppShell />
  </RequireAuth>
);

export const router = createBrowserRouter([
  // Login route lives outside the auth wrapper but still uses AppShell so
  // the navbar is visible (with no user — see Navbar.jsx).
  {
    element: <AppShell />,
    children: [{ path: '/auth/login', element: <LoginPage /> }],
  },
  {
    element: protectedShell,
    children: [
      { path: '/', element: <Navigate to="/feed" replace /> },
      { path: '/feed', element: <FeedPage /> },
      { path: '/reading-list', element: <ReadingListPage /> },
      { path: '/profile', element: <ProfilePage /> },
      { path: '/papers/:id', element: <PaperDetailPage /> },
    ],
  },
]);
// [GenAI Usage] Response Ends
// [GenAI Reflection] I used Claude Code to scaffold this because the two-tree structure (one
// AppShell for the public login route, a second AppShell wrapped in RequireAuth for everything
// else) wasn't obvious to me at first. My first instinct was to put RequireAuth around the
// whole router, but that would've also blocked /auth/login and caused a redirect loop. Splitting
// it into two top-level route objects that both render AppShell fixed that. I tested by signing
// out and confirming /feed bounces to /auth/login while /auth/login itself stays reachable.
