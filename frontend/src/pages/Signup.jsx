import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserPlus, Loader2, AlertCircle, CheckCircle } from 'lucide-react';

export default function Signup() {
  const { signUp } = useAuth();
  const navigate = useNavigate();

  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const validatePassword = (pwd) => {
    if (pwd.length < 6) return 'Password must be at least 6 characters long.';
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (password !== confirmPassword) {
      setError('Passwords do not match. Please ensure both password fields are identical.');
      return;
    }

    const pwdError = validatePassword(password);
    if (pwdError) {
      setError(pwdError);
      return;
    }

    if (!displayName.trim()) {
      setError('Please enter a display name.');
      return;
    }

    setIsLoading(true);

    try {
      const { user } = await signUp({
        email,
        password,
        displayName: displayName.trim(),
      });

      if (user && user.identities?.length === 0) {
        setError('An account with this email already exists. Please sign in instead.');
      } else if (!user) {
        setSuccess(
          'Verification email sent! Please check your inbox and click the confirmation link, then sign in.'
        );
      } else {
        navigate('/tutor', { replace: true });
      }
    } catch (err) {
      const msg = err?.message || 'Sign-up failed';
      if (/already registered|user already exists/i.test(msg)) {
        setError('An account with this email already exists. Please sign in instead.');
      } else if (/weak password|password/i.test(msg)) {
        setError(msg || 'Please choose a stronger password.');
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
            Create your account and start learning today.
          </p>
        </div>

        {error && (
          <div className="error-banner" style={{ marginBottom: 20 }}>
            <AlertCircle size={16} />
            <div>{error}</div>
          </div>
        )}

        {success && (
          <div
            style={{
              background: 'rgba(16,185,129,0.1)',
              border: '1px solid var(--success)',
              color: '#6ee7b7',
              padding: '12px 16px',
              borderRadius: 10,
              fontSize: 13,
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              marginBottom: 20,
            }}
          >
            <CheckCircle size={16} />
            <div>{success}</div>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <label
              htmlFor="displayName"
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
              Display Name
            </label>
            <input
              id="displayName"
              type="text"
              autoComplete="nickname"
              required
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="How should we call you?"
              className="chat-input"
              style={{ width: '100%', padding: '10px 14px', fontSize: 14 }}
              disabled={isLoading}
              maxLength={50}
            />
          </div>

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
              autoComplete="new-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 6 characters"
              className="chat-input"
              style={{ width: '100%', padding: '10px 14px', fontSize: 14 }}
              disabled={isLoading}
              minLength={6}
            />
          </div>

          <div>
            <label
              htmlFor="confirmPassword"
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
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              autoComplete="new-password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Re-enter your password"
              className="chat-input"
              style={{ width: '100%', padding: '10px 14px', fontSize: 14 }}
              disabled={isLoading}
              minLength={6}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={isLoading || !displayName || !email || !password || !confirmPassword}
            style={{ marginTop: 8, padding: '12px 20px' }}
          >
            {isLoading ? (
              <>
                <Loader2 size={16} style={{ animation: 'spin 0.8s linear infinite' }} />
                Creating account...
              </>
            ) : (
              <>
                <UserPlus size={16} />
                Create Account
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
            Already have an account?{' '}
            <Link
              to="/login"
              style={{
                color: 'var(--accent-primary)',
                fontWeight: 600,
                textDecoration: 'none',
              }}
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
