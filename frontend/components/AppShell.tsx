'use client';

import type { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { AuthGuard, useAuth } from './auth';

function ThemeSettings() {
  const [open, setOpen] = useState(false);
  const [theme, setTheme] = useState<'system' | 'light' | 'dark'>('dark');
  useEffect(() => { const saved = window.localStorage.getItem('route53-theme') as 'system' | 'light' | 'dark' | null; const next = saved || 'dark'; setTheme(next); document.documentElement.dataset.theme = next; }, []);
  function select(next: 'system' | 'light' | 'dark') { setTheme(next); window.localStorage.setItem('route53-theme', next); document.documentElement.dataset.theme = next; }
  return <span className="theme-settings"><button className="theme-settings-button" aria-label="Settings" onClick={() => setOpen(value => !value)}><span className="icon">⚙</span></button>{open && <div className="theme-menu"><h3>Current user settings</h3><strong>Visual mode <em>- beta</em></strong>{(['system', 'light', 'dark'] as const).map(value => <label key={value}><input type="radio" name="theme" checked={theme === value} onChange={() => select(value)} /> {value === 'system' ? 'Browser default' : value[0].toUpperCase() + value.slice(1)}</label>)}</div>}</span>;
}

function Icon({ name }: { name: 'grid'|'terminal'|'bell'|'help'|'settings'|'info'|'menu' }) {
  const paths = { grid: 'M4 4h4v4H4zM10 4h4v4h-4zM4 10h4v4H4zM10 10h4v4h-4z', terminal: 'M3 4h12v10H3zM5 7l2 2-2 2m4 0h3', bell: 'M5 12h6l-1-2V7a2 2 0 0 0-4 0v3l-1 2zm2 1a1 1 0 0 0 2 0', help: 'M8 14a6 6 0 1 0 0-12 6 6 0 0 0 0 12zm-1.3-7.4a1.5 1.5 0 1 1 2.5 1.1c-.7.5-1.2.8-1.2 1.8m0 2.2h.01', settings: 'M8 5.3a2.7 2.7 0 1 0 0 5.4 2.7 2.7 0 0 0 0-5.4zM8 2v1.3m0 9.4V14M2 8h1.3m9.4 0H14M3.8 3.8l.9.9m6.6 6.6.9.9m0-8.4-.9.9m-6.6 6.6-.9.9', info: 'M8 14a6 6 0 1 0 0-12 6 6 0 0 0 0 12zM8 7v3m0-5h.01', menu: 'M2 4h12M2 8h12M2 12h12' } as const;
  if (name === 'settings') return <ThemeSettings />;
  return <svg className="icon" viewBox="0 0 16 16" aria-hidden="true"><path d={paths[name]} /></svg>;
}

const groups = [['', [['Dashboard','/dashboard'],['Hosted zones','/hosted-zones'],['Health checks','/health-checks'],['Profiles','/profiles']]],['Global Resolver',[['Global resolvers','#'],['Shared DNS views','#']]],['VPC Resolver',[['VPCs','#'],['Inbound endpoints','#'],['Outbound endpoints','#'],['Rules','#'],['Query logging','#'],['Outposts','#']]],['Domains',[['Registered domains','#'],['Requests','#']]],['IP-based routing',[['CIDR collections','#']]],['Traffic flow',[['Traffic policies','/traffic-policies'],['Policy records','#']]]];

export function AppShell({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});
  const [navOpen, setNavOpen] = useState(true);
  const currentLabel = pathname.startsWith('/hosted-zones/create') ? 'Create hosted zone' : pathname.startsWith('/hosted-zones/') && pathname.endsWith('/records/create') ? 'Create record' : pathname.startsWith('/hosted-zones/') ? 'Hosted zone details' : pathname === '/hosted-zones' ? 'Hosted zones' : pathname === '/traffic-policies' ? 'Traffic policies' : pathname === '/health-checks' ? 'Health checks' : pathname === '/profiles' ? 'Profiles' : pathname === '/resolver' ? 'Resolver' : 'Dashboard';

  if (pathname === '/login' || pathname === '/signup') return <AuthGuard>{children}</AuthGuard>;
  return <AuthGuard><div className={`app ${navOpen ? '' : 'sidebar-collapsed'}`}>
    <div className="global-header"><img className="aws-logo" src="/aws-logo.png" alt="AWS"/><img className="route53-mark" src="/route53-mark.png" alt="Route 53"/><span className="grid" aria-hidden="true"><Icon name="grid" /></span><div className="global-search" role="search"><span className="search-mark">⌕</span> Search <kbd>[Alt+S]</kbd></div><div className="utilities"><Icon name="terminal"/><Icon name="bell"/><Icon name="help"/><Icon name="settings"/><span className="region">Global ▾</span><span className="account">{user?.username} <small>(development account)</small><button className="logout-btn" onClick={() => void logout()}>Logout</button></span></div></div>
    <div className="crumb-bar"><button className={`hamb ${navOpen ? '' : 'collapsed'}`} aria-label={navOpen ? 'Collapse navigation' : 'Expand navigation'} aria-expanded={navOpen} onClick={() => setNavOpen(open => !open)}><Icon name="menu" /></button><Link href="/dashboard">Route 53</Link><span className="crumb-sep">›</span><strong>{currentLabel}</strong><span className="crumb-info"><Icon name="info" /></span></div>
    <div className="body">{navOpen && <aside aria-label="Route 53 navigation"><h2>Route 53 <span aria-hidden="true">‹</span></h2>{groups.map(([title, items]) => <div className="side-group" key={title as string}>{title && <button className="side-group-toggle" onClick={() => setCollapsed(c => ({ ...c, [title as string]: !c[title as string] }))} aria-expanded={!collapsed[title as string]}><span className="disclosure">▾</span> {title as string}</button>}{!collapsed[title as string] && (items as string[][]).map(([label, href]) => <Link className={pathname === href || (href !== '#' && pathname.startsWith(href + '/')) ? 'active' : ''} href={href} key={label}>{label}{(label === 'Global resolvers' || label === 'Shared DNS views') && <em>New</em>}</Link>)}</div>)}</aside>}<main>{children}</main></div>
    <footer><span className="aws-footer-links"><a href="#"><img src="/cloudshell.svg" alt="" />CloudShell</a><a href="#"><img src="/agent-toolkit.svg" alt="" />Agent Toolkit for AWS</a><a href="#">Feedback</a><a href="#"><img src="/console-mobile.svg" alt="" />Console Mobile App</a></span><span>© 2026, Amazon Web Services, Inc.　 Privacy　 Terms　 Cookie preferences</span></footer>
  </div></AuthGuard>;
}
