'use client';

import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';
import { ApiError, dnsRecordsApi, DNSRecord, hostedZonesApi } from '../../../../services/api';
import { Notice } from '../../../../components/Notice';
import { LoadingState, Panel } from '../../../../components/ui';

const previewValue = (record: DNSRecord) => record.type === 'MX' ? `${record.priority ?? 0} ${record.value}` : record.type === 'SRV' ? `${record.priority ?? 0} ${record.weight ?? 0} ${record.port ?? 0} ${record.value}` : record.type === 'CAA' ? `${record.flag ?? 0} ${record.tag ?? ''} "${record.value}"` : record.value;

export default function ImportZoneFilePage() {
  const { id: rawId } = useParams<{ id: string }>();
  const id = Number(rawId);
  const router = useRouter();
  const [zoneName, setZoneName] = useState('hosted zone');
  const [text, setText] = useState('');
  const [preview, setPreview] = useState<DNSRecord[]>([]);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [loaded, setLoaded] = useState(false);
  useEffect(() => { void hostedZonesApi.get(id).then(zone => { setZoneName(zone.name); setLoaded(true); }).catch(() => setLoaded(true)); }, [id]);
  useEffect(() => { const timer = window.setTimeout(() => { if (!text.trim()) { setPreview([]); return; } void dnsRecordsApi.previewImport(id, text).then(result => { setPreview(result.records); setError(''); }).catch(reason => { setPreview([]); const err = reason as ApiError; setError(err.message || 'The zone file has validation errors.'); }); }, 250); return () => window.clearTimeout(timer); }, [id, text]);
  const filtered = useMemo(() => preview.filter(record => `${record.name} ${record.type} ${previewValue(record)} ${record.ttl}`.toLowerCase().includes(search.toLowerCase())), [preview, search]);
  async function importRecords() { setError(''); setSaving(true); try { const result = await dnsRecordsApi.import(id, text); router.replace(`/hosted-zones/${id}?imported=${result.imported_count}`); } catch (reason) { const err = reason as ApiError; setError(err.message || 'Unable to import the zone file.'); } finally { setSaving(false); } }
  if (!loaded) return <LoadingState label="Loading hosted zone…" />;
  return <><div className="detail-breadcrumb"><Link href="/dashboard">Route 53</Link><span>›</span><Link href="/hosted-zones">Hosted zones</Link><span>›</span><Link href={`/hosted-zones/${id}`}>{zoneName}</Link><span>›</span><strong>Import zone file</strong></div><div className="page-heading"><div><h1>Import zone file <a className="info">Info</a></h1><p className="page-description">You can create records for a Route 53 hosted zone by importing a zone file.</p></div></div>{error && <Notice kind="error">{error}</Notice>}<Panel className="import-zone-panel"><h2>Zone file</h2><p>Paste the contents of your zone file below.</p><textarea className="field import-textarea" value={text} onChange={event => setText(event.target.value)} placeholder={'subdomain1 300 A 10.0.0.0\nsubdomain2 300 CNAME example.com.'} /><small>If the hosted zone already contains records that appear in the zone file, the import process fails, and no records are created. Enter multiple records on separate lines.</small></Panel><Panel className="import-preview"><h2>Record preview for ({preview.length})</h2><div className="search-input record-search"><span>⌕</span><input value={search} onChange={event => setSearch(event.target.value)} placeholder="Filter records by property or value" /></div>{filtered.length ? <div className="record-table"><div className="table-head import-record-head"><span>Record name</span><span>Type</span><span>Value/Route traffic to</span><span>TTL (seconds)</span></div>{filtered.map((record, index) => <div className="record-row import-record-row" key={`${record.name}-${record.type}-${index}`}><span>{record.name}</span><span>{record.type}</span><span className="record-value">{previewValue(record)}</span><span>{record.ttl}</span></div>)}</div> : <div className="record-notice"><strong>{preview.length ? 'No records match the filter.' : 'This table displays records based on the contents of your zone file.'}</strong></div>}</Panel><div className="form-actions import-actions"><button type="button" className="secondary-btn" onClick={() => router.back()}>Cancel</button><button type="button" className="primary-btn" disabled={saving || preview.length === 0} onClick={() => void importRecords()}>{saving ? 'Importing…' : 'Import'}</button></div></>;
}
