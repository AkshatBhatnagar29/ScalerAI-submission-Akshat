'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ApiError, hostedZonesApi, ZoneType } from '../../../services/api';
import { Notice } from '../../../components/Notice';
import { Panel } from '../../../components/ui';

export default function CreateHostedZone() {
  const router = useRouter();
  const [type, setType] = useState<ZoneType>('PUBLIC');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    const data = new FormData(event.currentTarget);
    const name = String(data.get('name') || '').trim();
    const description = String(data.get('description') || '').trim();
    if (!name) return setError('Domain name is required.');
    if (!name.includes('.')) return setError('Enter a valid domain name, such as example.com.');
    setBusy(true);
    try {
      await hostedZonesApi.create({ name, type, description: description || null });
      router.replace('/hosted-zones?created=1');
    } catch (reason) {
      const failure = reason as ApiError;
      if (failure.status === 401) router.replace('/login');
      else setError(failure.status === 409 ? 'A hosted zone with this name and type already exists.' : failure.status === 422 ? 'Please check the highlighted fields.' : failure.message);
      setBusy(false);
    }
  }

  return <form className="create-zone-page" onSubmit={submit}>
    <div className="page-heading"><div><h1>Create hosted zone <a className="info" aria-label="Hosted zone information">Info</a></h1><p className="page-description">Create a container for DNS records and routing information for a domain.</p></div></div>
    {error && <Notice kind="error">{error}</Notice>}
    <Panel className="form-section">
      <h2>Hosted zone configuration</h2>
      <p>A hosted zone is a container that holds information about how you want to route traffic for a domain, such as example.com, and its subdomains.</p>
      <label htmlFor="zone-name">Domain name <a className="info">Info</a></label>
      <small>This is the name of the domain that you want to route traffic for.</small>
      <input id="zone-name" className="field" name="name" placeholder="example.com" required autoFocus />
      <small>Valid characters: a-z, 0-9, - _ .</small>
      <label htmlFor="zone-description">Description - optional <a className="info">Info</a></label>
      <small>This value lets you distinguish hosted zones that have the same name.</small>
      <textarea id="zone-description" className="field area" name="description" maxLength={2000} placeholder="The hosted zone is used for..." />
      <fieldset>
        <legend>Type <a className="info">Info</a></legend>
        <small>The type indicates whether you want to route traffic on the internet or in an Amazon VPC.</small>
        <div className="radio-row">
          <label className={`radio-card ${type === 'PUBLIC' ? 'selected' : ''}`}><input type="radio" checked={type === 'PUBLIC'} onChange={() => setType('PUBLIC')} name="type" value="PUBLIC" /><span><b>Public hosted zone</b><small>A public hosted zone determines how traffic is routed on the internet.</small></span></label>
          <label className={`radio-card ${type === 'PRIVATE' ? 'selected' : ''}`}><input type="radio" checked={type === 'PRIVATE'} onChange={() => setType('PRIVATE')} name="type" value="PRIVATE" /><span><b>Private hosted zone</b><small>A private hosted zone determines how traffic is routed within an Amazon VPC.</small></span></label>
        </div>
      </fieldset>
    </Panel>
    <Panel className="form-section tags-section">
      <h2>Tags <a className="info">Info</a></h2>
      <p>Apply tags to hosted zones to help organize and identify them.</p>
      <p className="tag-empty">No tags associated with the resource.</p>
      <button type="button" className="outline-btn tag-disabled" disabled>Add tag</button>
      <small>Tag management is outside this project phase.</small>
    </Panel>
    <div className="form-actions create-actions"><button type="button" className="secondary-btn" onClick={() => router.push('/hosted-zones')}>Cancel</button><button className="primary-btn" disabled={busy}>{busy ? 'Creating...' : 'Create hosted zone'}</button></div>
  </form>;
}
