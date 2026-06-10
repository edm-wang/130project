// [GenAI Usage] Prompt: This is the entry point for the React app I'm migrating from the static
// HTML pages. I want it to mount a single root, pull in the global reset/tokens CSS so every
// page gets the same baseline, and hand off all page rendering to a router instead of me writing
// separate index.html files per page. Set it up with createBrowserRouter via a router.jsx file
// and wrap the whole thing in StrictMode.
// [GenAI Usage] Response Starts:
import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';

import './styles/reset.css';
import './styles/tokens.css';
import { router } from './router.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
// [GenAI Usage] Response Ends
// [GenAI Reflection] I used Claude Code for this because I'd never set up a Vite + React Router
// project from scratch before and didn't want to get the bootstrap wrong. The two CSS imports
// (reset.css, tokens.css) matter, since without them the migrated pages looked completely
// unstyled because the old HTML pages had a shared <link> tag I hadn't ported over yet. I
// double-checked that #root actually exists in index.html before trusting this would render
// anything.
