import type { ReactNode } from 'react';
import './globals.css';
import { AppShell } from '../components/AppShell';
import { AuthProvider } from '../components/auth';

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="en"><body><AuthProvider><AppShell>{children}</AppShell></AuthProvider></body></html>;
}
