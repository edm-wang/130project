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
