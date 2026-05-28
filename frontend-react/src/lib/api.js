/**
 * Thin wrapper around the FastAPI backend.
 *
 * Auth: `Authorization: Bearer <Supabase JWT>`.
 *   Token resolution order:
 *     1. ?token= URL override (handy for demos)
 *     2. Active Supabase session
 *     3. localStorage.pa_access_token  (legacy fallback for the old HTML mocks)
 *
 * Backend URL precedence: localStorage.pa_backend_url > VITE_BACKEND_URL > localhost:8000.
 */

import { hasSupabaseConfig, supabase } from './supabase.js';

const DEFAULT_BACKEND_URL = 'http://localhost:8000';

export function getBackendUrl() {
  const fromLs =
    typeof localStorage !== 'undefined' && localStorage.getItem('pa_backend_url');
  const fromEnv = import.meta.env.VITE_BACKEND_URL;
  const url = fromLs || fromEnv || DEFAULT_BACKEND_URL;
  return String(url).replace(/\/$/, '');
}

/**
 * Returns the current access token, or '' if there is none. Async because
 * Supabase's getSession() is async.
 */
export async function getAccessToken() {
  if (typeof window !== 'undefined') {
    const fromUrl = new URLSearchParams(window.location.search).get('token');
    if (fromUrl) return fromUrl;
  }
  if (hasSupabaseConfig) {
    const { data } = await supabase.auth.getSession();
    if (data.session && data.session.access_token) return data.session.access_token;
  }
  if (typeof localStorage !== 'undefined') {
    return localStorage.getItem('pa_access_token') || '';
  }
  return '';
}

export function isMockMode() {
  // Vite's import.meta.env values are strings, not booleans.
  return import.meta.env.VITE_USE_MOCK_DATA === 'true';
}

// [GenAI Usage] Prompt:
// Add a shared apiFetch helper and new fetch functions (fetchProfile, saveProfile,
// fetchInterests, addInterest, deleteInterest, fetchSavedPapers) to api.js, following
// the same Bearer token attachment and error code pattern as the existing fetchRecommendations.
// [GenAI Usage] Response Starts:

/**
 * Shared fetch helper: attaches Bearer token, normalises error codes.
 * @param {string} path  — path relative to backend root, e.g. '/users/me'
 * @param {RequestInit} [options]
 */
async function apiFetch(path, options = {}) {
  const token = await getAccessToken();
  if (!token) {
    const err = new Error('Not signed in.');
    err.code = 'NO_TOKEN';
    throw err;
  }
  const headers = { Authorization: `Bearer ${token}`, ...options.headers };
  let res;
  try {
    res = await fetch(`${getBackendUrl()}${path}`, { ...options, headers });
  } catch (cause) {
    const err = new Error(`Could not reach backend at ${getBackendUrl()}. Is it running?`);
    err.code = 'NETWORK';
    err.cause = cause;
    throw err;
  }
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    const err = new Error(`Backend returned ${res.status}${text ? `: ${text}` : `: ${res.statusText}`}`);
    err.code =
      res.status === 401 ? 'UNAUTHORIZED'
      : res.status === 404 ? 'NOT_FOUND'
      : res.status === 409 ? 'CONFLICT'
      : 'HTTP_ERROR';
    err.status = res.status;
    throw err;
  }
  return res;
}

/** GET /recommendations. Throws on non-2xx or missing token. */
export async function fetchRecommendations() {
  const token = await getAccessToken();
  if (!token) {
    const err = new Error('Not signed in.');
    err.code = 'NO_TOKEN';
    throw err;
  }
  let res;
  try {
    res = await fetch(`${getBackendUrl()}/recommendations`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (cause) {
    const err = new Error(
      `Could not reach backend at ${getBackendUrl()}. Is it running?`,
    );
    err.code = 'NETWORK';
    err.cause = cause;
    throw err;
  }
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    const err = new Error(
      `Backend returned ${res.status}${text ? `: ${text}` : `: ${res.statusText}`}`,
    );
    err.code = res.status === 401 ? 'UNAUTHORIZED' : 'HTTP_ERROR';
    err.status = res.status;
    throw err;
  }
  return res.json();
}

/** GET /users/me. Returns { profile } — profile is null if the user has no row yet. */
export async function fetchProfile() {
  const res = await apiFetch('/users/me');
  return res.json();
}

/** PUT /users/me. Upserts profile. Returns { profile }. */
export async function saveProfile(payload) {
  const res = await apiFetch('/users/me', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return res.json();
}

/** GET /users/me/interests. Returns { interests: [...] }. */
export async function fetchInterests() {
  const res = await apiFetch('/users/me/interests');
  return res.json();
}

/** POST /users/me/interests. Returns the created interest row. */
export async function addInterest(value, interest_type) {
  const res = await apiFetch('/users/me/interests', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ value, interest_type }),
  });
  return res.json();
}

/** DELETE /users/me/interests/:id. Returns { deleted: id }. */
export async function deleteInterest(interestId) {
  const res = await apiFetch(`/users/me/interests/${interestId}`, { method: 'DELETE' });
  return res.json();
}

/** GET /saved-papers. Returns { saved_papers: [...] }. */
export async function fetchSavedPapers() {
  const res = await apiFetch('/saved-papers');
  return res.json();
}
// [GenAI Usage] Response Ends
// [GenAI Usage] Reflection:
// I used Claude Code to generate the new API functions because they are highly repetitive wrappers
// around the same fetch pattern. Extracting a shared apiFetch helper first meant all six functions
// stay short and consistent. I reviewed the error code mapping (NO_TOKEN, NETWORK, UNAUTHORIZED,
// NOT_FOUND, CONFLICT, HTTP_ERROR) against the existing fetchRecommendations implementation and
// confirmed the Content-Type header is included on POST/PUT requests that send a JSON body.
