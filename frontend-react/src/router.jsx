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
