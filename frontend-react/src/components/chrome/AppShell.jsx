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
