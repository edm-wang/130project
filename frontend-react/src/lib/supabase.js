// [GenAI Usage] Prompt: Set up the Supabase client for the frontend, reading the URL and
// publishable key from Vite env vars (VITE_SUPABASE_URL, VITE_SUPABASE_PUBLISHABLE_KEY). I want
// one shared client instance instead of creating a new one in every file that needs it. Also,
// since teammates might pull this branch without the .env.development file set up yet, the app
// shouldn't throw on import if those vars are missing. Export a flag so other code can check
// before calling anything on the client.
// [GenAI Usage] Response Starts:
import { createClient } from '@supabase/supabase-js';

/**
 * Singleton browser Supabase client. Reads VITE_SUPABASE_URL and
 * VITE_SUPABASE_PUBLISHABLE_KEY from .env.development.
 *
 * `hasSupabaseConfig` lets callers degrade gracefully if the env vars
 * aren't set — useful when the UI is being demoed without a backend.
 */

const url = import.meta.env.VITE_SUPABASE_URL || '';
const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || '';

export const hasSupabaseConfig = Boolean(url && key);

export const supabase = hasSupabaseConfig
  ? createClient(url, key, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    })
  : null;
// [GenAI Usage] Response Ends
// [GenAI Reflection] I asked Claude Code for the hasSupabaseConfig guard specifically because
// createClient('', '') doesn't fail loudly. It just creates a client that fails on every call,
// which would've been a confusing way to discover a missing .env file. Returning null and
// checking hasSupabaseConfig everywhere (useAuth, LoginPage) makes the "not configured" state
// explicit instead of something you only notice after a network call mysteriously errors out.
// I kept persistSession/autoRefreshToken/detectSessionInUrl at their defaults-ish values since
// that's what Supabase recommends for browser SPAs.
