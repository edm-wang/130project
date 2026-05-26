import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Port 3000 matches the FastAPI backend's CORS allowlist
// (see backend/app/main.py: allow_origins=['http://localhost:3000']).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    strictPort: true,
  },
});
