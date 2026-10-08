import type { ReactNode } from 'react';

export function Panel({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <section className={`panel ${className}`}>{children}</section>;
}

export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return <Panel className="empty-zone"><p>{label}</p></Panel>;
}

export function SearchInput({ placeholder }: { placeholder: string }) {
  return <div className="search-input"><span aria-hidden="true">⌕</span><input placeholder={placeholder} /></div>;
}
