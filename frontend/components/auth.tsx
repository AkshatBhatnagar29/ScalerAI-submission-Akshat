'use client';

import { createContext, FormEvent, ReactNode, useContext, useEffect, useMemo, useState } from 'react';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';

// Use the same-origin Next.js API proxy so the session cookie is reliable on localhost/127.0.0.1.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';
export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';
export type User = { username: string };
type AuthContextValue = { status: AuthStatus; user: User | null; login: (username: string, password: string) => Promise<{ ok: boolean; message?: string }>; logout: () => Promise<void> };
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>('loading');
  const [user, setUser] = useState<User | null>(null);
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/auth/me`, { credentials: 'include' }).then(async response => {
      if (!response.ok) throw new Error('unauthenticated');
      return response.json();
    }).then(data => { setUser(data.user); setStatus('authenticated'); }).catch(() => { setUser(null); setStatus('unauthenticated'); });
  }, []);
  const value = useMemo<AuthContextValue>(() => ({
    status, user,
    login: async (username, password) => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password }) });
        if (!response.ok) return { ok: false, message: response.status === 401 ? 'Incorrect username or password.' : 'Unable to sign in right now.' };
        const data = await response.json(); setUser(data.user); setStatus('authenticated'); return { ok: true };
      } catch { return { ok: false, message: 'The authentication service is unavailable. Please try again.' }; }
    },
    logout: async () => { try { await fetch(`${API_BASE_URL}/api/auth/logout`, { method: 'POST', credentials: 'include' }); } catch { /* local state is still cleared */ } setUser(null); setStatus('unauthenticated'); },
  }), [status, user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() { const context = useContext(AuthContext); if (!context) throw new Error('useAuth must be used inside AuthProvider'); return context; }

export function AuthGuard({ children }: { children: ReactNode }) {
  const { status } = useAuth(); const pathname = usePathname(); const router = useRouter(); const isAuthPage = pathname === '/login' || pathname === '/signup';
  useEffect(() => { if (status === 'unauthenticated' && !isAuthPage) router.replace(`/login?next=${encodeURIComponent(pathname)}`); if (status === 'authenticated' && isAuthPage) router.replace('/dashboard'); }, [isAuthPage, pathname, router, status]);
  if (status === 'loading' || (!isAuthPage && status !== 'authenticated') || (isAuthPage && status === 'authenticated')) return <div className="auth-loading" role="status">Checking your Route 53 session…</div>;
  return <>{children}</>;
}

export function LoginForm() {
  const { login } = useAuth(); const router = useRouter(); const searchParams = useSearchParams(); const [username, setUsername] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState(''); const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); if (busy) return; setError(''); setBusy(true); const result = await login(username, password); if (result.ok) { const next = searchParams.get('next'); router.replace(next && next.startsWith('/') ? next : '/dashboard'); } else setError(result.message || 'Unable to sign in right now.'); setBusy(false); }
  return <form className="login-card" onSubmit={submit}><div className="login-brand"><img src="/route53-mark.svg" alt="" /><div><strong>Route 53</strong><span>Web Services Console</span></div></div><h1>Sign in</h1><p className="login-intro">Sign in to the Route 53 console.</p>{error && <div className="login-error" role="alert">{error}</div>}<label htmlFor="username">Username</label><input id="username" className="field" value={username} onChange={event => setUsername(event.target.value)} autoComplete="username" required /><label htmlFor="password">Password</label><input id="password" type="password" className="field" value={password} onChange={event => setPassword(event.target.value)} autoComplete="current-password" required /><button className="primary-btn login-submit" type="submit" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button><small>Use the configured development mock credentials.</small><div className="login-switch">New to Route 53? <Link href="/signup">Create an account</Link></div></form>;
}
