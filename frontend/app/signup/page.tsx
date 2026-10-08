import Link from 'next/link';

export default function SignupPage() {
  return <div className="login-page"><div className="login-header"><img src="/aws-logo.svg" alt="AWS" /><span>Console Sign-In</span></div><div className="login-card"><div className="login-brand"><img src="/route53-mark.svg" alt="" /><div><strong>Route 53</strong><span>Web Services Console</span></div></div><h1>Create account</h1><p className="login-intro">Account creation is not enabled for this development mock. Use the provided mock account to enter the Route 53 console.</p><div className="login-error login-notice">Use the development credentials on the sign-in page.</div><Link className="primary-btn login-submit login-link-button" href="/login">Go to sign in</Link><div className="login-switch">Already have an account? <Link href="/login">Sign in</Link></div></div></div>;
}
