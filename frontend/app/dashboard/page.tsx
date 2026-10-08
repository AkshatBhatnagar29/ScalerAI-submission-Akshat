import Link from 'next/link';
import { Panel } from '../../components/ui';

export default function Dashboard() {
  return <>
    <h1>Route 53 Dashboard <a className="info">Info</a></h1>
    <Panel className="dashboard-placeholder">
      <h2>Route 53 console</h2>
      <p>This project currently focuses on hosted zones and DNS records. Additional Route 53 services will be available in a later phase.</p>
      <div className="dashboard-links"><Link className="primary-btn" href="/hosted-zones">View hosted zones</Link><Link className="secondary-btn" href="/hosted-zones/create">Create hosted zone</Link></div>
    </Panel>
    <Panel className="coming"><h2>Coming soon</h2><p>Health checks, traffic policies, resolver, profiles, and domain registration remain visual placeholders.</p></Panel>
  </>;
}
