// [GenAI Usage] Prompt: Every one of the four static pages (feed, reading list, profile, paper
// detail) has the same navbar at the top and basically just swaps out the content underneath.
// Make a layout component for react-router-dom that renders the navbar once and lets whatever
// the current route is render below it, so I'm not copy-pasting the Navbar import into every
// page component.
// [GenAI Usage] Response Starts:
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar.jsx';

/**
 * Layout route. Renders the shared top navigation and lets the active
 * page render into <Outlet />.
 */
export default function AppShell() {
  return (
    <div>
      <Navbar />
      <Outlet />
    </div>
  );
}
// [GenAI Usage] Response Ends
// [GenAI Reflection] This one is tiny but I still ran it through Claude Code because I wasn't
// sure whether <Outlet /> needed a wrapper element or any specific props to work with
// createBrowserRouter's nested routes. Turned out to be this simple. I plugged it into
// router.jsx as the layout for both the public login route and the protected route group, and
// confirmed the navbar shows up consistently across all four pages without each page needing
// to import it separately.
