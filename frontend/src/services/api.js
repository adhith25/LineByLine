/**
 * LineByLine API Client Service
 * Connects React frontend components to Flask REST endpoints.
 *
 * Phase 7B updates:
 *  - Every request attaches `Authorization: Bearer <access_token>`
 *    from the Supabase session (if one is available — handled via
 *    getAuthHeaders() at call-time so we always have the latest token).
 *  - 401 responses trigger a soft redirect to /login via an authenticated
 *    event that the Auth layer can observe (see window.postMessage pattern).
 *
 * Provides:
 *  - Retry logic for transient network/5xx failures (GET endpoints).
 *  - User-friendly error messages that avoid exposing raw internals.
 *  - Consistent request/response handling across all endpoints.
 */

import { supabase } from './supabaseClient';

const RETRYABLE_STATUS = new Set([408, 429, 500, 502, 503, 504]);
const MAX_RETRIES = 2;
const BASE_DELAY_MS = 650;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function getAuthHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  try {
    const { data } = await supabase.auth.getSession();
    const token = data?.session?.access_token;
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  } catch (_err) {
    // If Supabase client isn't available yet, just skip the header.
    // Backend will gracefully return 401/503 as appropriate.
  }
  return headers;
}

function notifyAuthFailure(reason) {
  try {
    window.dispatchEvent(new CustomEvent('lbl:auth-required', { detail: { reason } }));
  } catch (_err) {
    /* no-op in non-browser env */
  }
}

function userFriendlyError(status, fallback) {
  switch (status) {
    case 0:
      return 'Cannot reach the backend server. Please make sure the Flask app is running on port 5000.';
    case 400:
      return fallback || 'Invalid request. Please check your input and try again.';
    case 401:
      return 'Your session has expired. Please sign in again to continue.';
    case 403:
      return 'You are not authorized to perform this action.';
    case 404:
      return 'The requested endpoint was not found. The server may need a restart.';
    case 408:
    case 504:
      return 'The request timed out. Gemini may be slow — please try again in a moment.';
    case 413:
      return 'Your code snippet is too large. Please trim it and try again.';
    case 429:
      return 'Too many requests. Please wait a few seconds before trying again.';
    case 503:
      return 'Server authentication layer is not ready. Please configure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY on the backend, then restart Flask.';
    case 500:
    case 502:
      return 'The backend hit an unexpected error. Please try again or restart the Flask server.';
    default:
      return fallback || `Request failed (status ${status}). Please try again.`;
  }
}

async function requestWithRetry(url, options, { retriable = true } = {}) {
  let lastError;
  const attempts = retriable ? MAX_RETRIES + 1 : 1;

  for (let i = 0; i < attempts; i++) {
    try {
      const authHeaders = await getAuthHeaders();
      const mergedOptions = {
        ...options,
        headers: {
          ...authHeaders,
          ...(options?.headers || {}),
        },
      };

      const response = await fetch(url, mergedOptions);

      if (response.ok) {
        return response.json();
      }

      const status = response.status;
      const errData = await response.json().catch(() => ({}));
      const message = errData.error || userFriendlyError(status);

      if (status === 401) {
        notifyAuthFailure(errData.code || 'EXPIRED');
      }

      if (retriable && RETRYABLE_STATUS.has(status) && i < attempts - 1 && status !== 401) {
        const delay = BASE_DELAY_MS * Math.pow(2, i);
        console.warn(`[api] Retrying ${url} after ${status} in ${delay}ms (attempt ${i + 2}/${attempts})`);
        await sleep(delay);
        lastError = new Error(message);
        continue;
      }

      const err = new Error(message);
      err.status = status;
      err.details = errData;
      throw err;
    } catch (err) {
      if (err.name === 'TypeError' && /failed to fetch|networkerror/i.test(err.message)) {
        const message = userFriendlyError(0);
        if (retriable && i < attempts - 1) {
          const delay = BASE_DELAY_MS * Math.pow(2, i);
          console.warn(`[api] Network error — retrying ${url} in ${delay}ms`);
          await sleep(delay);
          lastError = new Error(message);
          continue;
        }
        const networkErr = new Error(message);
        networkErr.status = 0;
        throw networkErr;
      }
      throw err;
    }
  }

  throw lastError || new Error('Request failed after retries.');
}

export async function explainCode({ code, mode, language }) {
  return requestWithRetry('/api/explain', {
    method: 'POST',
    body: JSON.stringify({ code, mode, language }),
  }, { retriable: false });
}

export async function teachConcept({ code, misconception, concept, mode, language }) {
  return requestWithRetry('/api/teach', {
    method: 'POST',
    body: JSON.stringify({ code, misconception, concept, mode, language }),
  }, { retriable: false });
}

export async function fetchConceptCheck({ code, concept, mode, language }) {
  return requestWithRetry('/api/concept-check', {
    method: 'POST',
    body: JSON.stringify({ code, concept, mode, language }),
  }, { retriable: false });
}

export async function fetchProgress() {
  return requestWithRetry('/api/progress', {
    method: 'GET',
  }, { retriable: true });
}

export async function submitQuizResult({ concept, isCorrect }) {
  return requestWithRetry('/api/quiz-result', {
    method: 'POST',
    body: JSON.stringify({ concept, is_correct: isCorrect }),
  }, { retriable: false });
}

export async function sendFollowup({ message, action, code, language, current_explanation }) {
  return requestWithRetry('/api/followup', {
    method: 'POST',
    body: JSON.stringify({ message, action, code, language, current_explanation }),
  }, { retriable: false });
}

export async function explainLine({ code, line, mode, language }) {
  return requestWithRetry('/api/line-explain', {
    method: 'POST',
    body: JSON.stringify({ code, line, mode, language }),
  }, { retriable: false });
}

export async function resetSession() {
  return requestWithRetry('/api/reset', {
    method: 'POST',
  }, { retriable: false });
}

export async function fetchRecommendations() {
  return requestWithRetry('/api/recommendations', {
    method: 'GET',
  }, { retriable: true });
}

export async function fetchMe() {
  return requestWithRetry('/api/me', {
    method: 'GET',
  }, { retriable: false });
}

export async function fetchSubmissions(limit = 50) {
  return requestWithRetry(`/api/submissions?limit=${limit}`, {
    method: 'GET',
  }, { retriable: true });
}

export async function fetchSubmissionDetail(id) {
  return requestWithRetry(`/api/submissions/${encodeURIComponent(id)}`, {
    method: 'GET',
  }, { retriable: true });
}

