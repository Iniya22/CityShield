/**
 * CityShield – API Service
 * Centralized HTTP helper with JWT auth headers
 */

const API_BASE = 'http://localhost:8000';

export function getToken() {
  return localStorage.getItem('cityshield_token');
}

export function getUser() {
  const data = localStorage.getItem('cityshield_user');
  return data ? JSON.parse(data) : null;
}

export function setAuth(token, username, role) {
  localStorage.setItem('cityshield_token', token);
  localStorage.setItem('cityshield_user', JSON.stringify({ username, role }));
}

export function clearAuth() {
  localStorage.removeItem('cityshield_token');
  localStorage.removeItem('cityshield_user');
}

export async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    clearAuth();
    window.location.hash = '#/login';
    throw new Error('Session expired');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'API error');
  }

  return res.json();
}

// Convenience methods
export const api = {
  get: (path) => apiFetch(path),
  post: (path, body) => apiFetch(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) => apiFetch(path, { method: 'PUT', body: JSON.stringify(body) }),
  del: (path) => apiFetch(path, { method: 'DELETE' }),
};
