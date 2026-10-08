'use client';
export function Notice({ kind, children }: { kind: 'success' | 'error'; children: React.ReactNode }) { return <div className={`notice ${kind}`} role={kind === 'error' ? 'alert' : 'status'}>{children}</div>; }
