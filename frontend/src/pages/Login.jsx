import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LogIn, Loader2, AlertCircle } from 'lucide-react';

export default function Login() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/tutor';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await signIn({ email, password });
      navigate(from, { replace: true });
    } catch (err) {
      const msg = err?.message || 'Login failed';
      if (/invalid/i.test(msg) || /email.*password/i.test(msg)) {
        setError('Invalid email or password. Please check your credentials and try again.');
      } else if (/email not confirmed/i.test(msg)) {
        setError('Please verify your email address before logging in.');
      } else {
        setError(msg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
        background: 'radial-gradient(ellipse at top, rgba(99,102,241,0.12) 0%, transparent 50%), var(--bg-dark)',
      }}
    >
      <div
        className="card-box"
        style={{
          width: '100%',
          maxWidth: 440,
          padding: '32px',
          boxShadow: '0 16px 48px rgba(0,0,0,0.5)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 10,
              marginBottom: 8,
            }}
          >
            <span className="brand-badge" style={{ fontSize: 16, padding: '6px 10px' }}>
              LBL
            </span>
            <span
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: 24,
                fontWeight: 700,
                background: 'linear-gradient(180deg, #ffffff 0%, #cbd5e1 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              LineByLine
            </span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 4 }}>
            Welcome back. Sign in to continue learning.
          </p>
        </div>

        {error && (
          <div className="error-banner" style={{ marginBottom: 20 }}>
            <AlertCircle size={16} />
            <div>{error}</div>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <label
              htmlFor="email"
              style={{
                display: 'block',
                fontSize: 12,
                fontWeight: 600,
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                letterSpacing: 0.5,
                marginBottom: 6,
              }}
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="chat-input"
              style={{ width: '100%', padding: '10px 14px', fontSize: 14 }}
              disabled={isLoading}
            />
          </div>

          <div>
            <label
              htmlFor="password"
              style={{
                display: 'block',
                fontSize: 12,
                fontWeight: 600,
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                letterSpacing: 0.5,
                marginBottom: 6,
              }}
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              className="chat-input"
              style={{ width: '100%', padding: '10px 14px', fontSize: 14 }}
              disabled={isLoading}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={isLoading || !email || !password}
            style={{ marginTop: 8, padding: '12px 20px' }}
          >
            {isLoading ? (
              <>
                <Loader2 size={16} style={{ animation: 'spin 0.8s linear infinite' }} />
                Signing in...
              </>
            ) : (
              <>
                <LogIn size={16} />
                Sign In
              </>
            )}
          </button>
        </form>

        <div
          style={{
            marginTop: 24,
            paddingTop: 20,
            borderTop: '1px solid var(--border-color)',
            textAlign: 'center',
          }}
        >
          <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
            New to LineByLine?{' '}
            <Link
              to="/signup"
              style={{
                color: 'var(--accent-primary)',
                fontWeight: 600,
                textDecoration: 'none',
              }}
            >
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
