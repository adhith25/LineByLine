import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { fetchMe, fetchProgress, fetchSubmissions, fetchRecommendations, resetSession } from '../services/api';
import LoadingState from '../components/common/LoadingState';
import MarkdownRenderer from '../components/MarkdownRenderer';
import { getMasteryCategory } from '../components/learning/MasteryBar';
import {
  User as UserIcon,
  Mail,
  LogOut,
  RotateCcw,
  Loader2,
  AlertCircle,
  Sparkles,
  Bot,
  Target,
  CheckCircle2,
  FileCode,
  Compass,
  ArrowRight,
  ShieldCheck,
  Award,
} from 'lucide-react';

export default function Profile() {
  const { user, displayName: authDisplayName, signOut, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [mounted, setMounted] = useState(false);

  // Me API state
  const [meData, setMeData] = useState(null);
  const [meLoading, setMeLoading] = useState(false);
  const [meError, setMeError] = useState(null);

  // Learning Snapshot state
  const [progressData, setProgressData] = useState(null);
  const [submissionsData, setSubmissionsData] = useState(null);
  const [recData, setRecData] = useState(null);
  const [snapshotLoading, setSnapshotLoading] = useState(false);
  const [snapshotError, setSnapshotError] = useState(null);

  // Action states
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [isResetting, setIsResetting] = useState(false);

  const loadMe = useCallback(async () => {
    setMeLoading(true);
    setMeError(null);
    try {
      const data = await fetchMe();
      setMeData(data);
    } catch (err) {
      console.warn('[Profile] GET /api/me failed, falling back to AuthContext:', err?.message || err);
      setMeError(err?.message || 'Unable to load account details from /api/me.');
    } finally {
      setMeLoading(false);
    }
  }, []);

  const loadSnapshot = useCallback(async () => {
    setSnapshotLoading(true);
    setSnapshotError(null);
    try {
      const [progRes, subRes, recRes] = await Promise.allSettled([
        fetchProgress(),
        fetchSubmissions(50),
        fetchRecommendations(),
      ]);

      if (progRes.status === 'fulfilled') setProgressData(progRes.value);
      if (subRes.status === 'fulfilled') setSubmissionsData(subRes.value);
      if (recRes.status === 'fulfilled') setRecData(recRes.value);

      if (progRes.status === 'rejected' && subRes.status === 'rejected') {
        setSnapshotError('Could not load learning metrics at this time.');
      }
    } catch (err) {
      setSnapshotError(err?.message || 'Failed to load learning snapshot.');
    } finally {
      setSnapshotLoading(false);
    }
  }, []);

  useEffect(() => {
    const t = setTimeout(() => setMounted(true), 30);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    if (!authLoading && user) {
      loadMe();
      loadSnapshot();
    }
  }, [authLoading, user, loadMe, loadSnapshot]);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await signOut();
      navigate('/login', { replace: true });
    } catch (err) {
      console.error('[Profile] Sign out failed:', err);
    } finally {
      setIsLoggingOut(false);
    }
  };

  const handleResetSession = async () => {
    setIsResetting(true);
    try {
      await resetSession();
      window.location.reload();
    } catch (err) {
      console.error('[Profile] Reset session failed:', err);
      alert('Failed to reset session. Please refresh the page manually.');
    } finally {
      setIsResetting(false);
    }
  };

  if (authLoading) {
    return <LoadingState message="Checking authentication…" fullHeight />;
  }

  // Identity resolution with fallback to AuthContext
  const resolvedName = meData?.display_name || authDisplayName || 'Learner';
  const resolvedEmail = meData?.email || user?.email || '—';
  const initials = (resolvedName || 'L')[0]?.toUpperCase() || 'L';

  // Derived real metrics
  const masteryList = progressData?.mastery || [];
  const totalSubmissions = submissionsData?.submissions?.length || 0;
  const conceptsPracticed = masteryList.length;
  const comfortableCount = masteryList.filter(
    (m) => getMasteryCategory(m.mastery_score) === 'comfortable'
  ).length;

  const primaryFocus = recData?.primary_concept;
  const recommendedAction = recData?.recommended_action;
  const rationale = recData?.rationale;

  return (
    <div className={`page-container${mounted ? ' page-in' : ''}`}>
      <header className="page-header">
        <div>
          <div className="page-kicker">
            <UserIcon size={14} aria-hidden="true" />
            <span>Account &amp; Insights</span>
          </div>
          <h1 className="page-title">Profile</h1>
          <p className="page-subtitle">
            Your LineByLine account details and personalized learning snapshot.
          </p>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20, maxWidth: 960 }}>
        {/* ACCOUNT INFORMATION CARD */}
        <div className="profile-card card-box" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 16, padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div className="profile-avatar" title={resolvedEmail}>
              {initials}
            </div>
            <div style={{ minWidth: 0 }}>
              <h2 className="profile-name">
                {meLoading && !resolvedName ? 'Loading…' : resolvedName}
              </h2>
              <div className="profile-email-row">
                <Mail size={14} aria-hidden="true" />
                <span className="profile-email">
                  {meLoading && !resolvedEmail ? 'Loading…' : resolvedEmail}
                </span>
              </div>
            </div>
          </div>

          {meError && (
            <div className="error-banner" style={{ marginTop: 16, fontSize: 12.5 }} role="alert">
              <AlertCircle size={15} aria-hidden="true" />
              <span>Could not refresh identity from /api/me — using authenticated session context.</span>
            </div>
          )}

          <div className="profile-divider" />

          <section aria-labelledby="account-details-heading">
            <h3 id="account-details-heading" className="profile-section-title">
              Authentication &amp; Security
            </h3>
            <ul className="profile-meta-list" aria-label="Account details">
              <li>
                <span className="profile-meta-label">Provider</span>
                <span className="profile-meta-value" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                  <ShieldCheck size={14} style={{ color: '#10b981' }} />
                  <span>Supabase Auth · JWT</span>
                </span>
              </li>
              <li>
                <span className="profile-meta-label">Role / Status</span>
                <span className="profile-meta-value">Authenticated Learner</span>
              </li>
              <li>
                <span className="profile-meta-label">Account ID</span>
                <span className="profile-meta-value mono" title={user?.id}>
                  {user?.id ? `${user.id.slice(0, 8)}…` : '—'}
                </span>
              </li>
            </ul>
          </section>

          <div className="profile-divider" />

          {/* ACCOUNT ACTIONS */}
          <div className="profile-actions" style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <button
              className="btn-secondary"
              onClick={handleResetSession}
              disabled={isResetting}
              style={{ width: 'auto', padding: '9px 16px', fontSize: 13 }}
            >
              {isResetting ? (
                <Loader2 size={14} style={{ animation: 'spin 0.8s linear infinite' }} aria-hidden="true" />
              ) : (
                <RotateCcw size={14} aria-hidden="true" />
              )}
              <span>{isResetting ? 'Resetting…' : 'Reset Session'}</span>
            </button>

            <button
              className="btn-secondary danger"
              onClick={handleLogout}
              disabled={isLoggingOut}
              style={{ width: 'auto', padding: '9px 16px', fontSize: 13 }}
            >
              {isLoggingOut ? (
                <Loader2 size={14} style={{ animation: 'spin 0.8s linear infinite' }} aria-hidden="true" />
              ) : (
                <LogOut size={14} aria-hidden="true" />
              )}
              <span>{isLoggingOut ? 'Signing out…' : 'Sign Out'}</span>
            </button>
          </div>
        </div>

        {/* LEARNING SNAPSHOT & CURRENT FOCUS */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* REAL LEARNING SNAPSHOT METRICS */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: 16,
              padding: '22px 24px',
              display: 'flex',
              flexDirection: 'column',
              gap: 14,
            }}
          >
            <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Award size={18} style={{ color: 'var(--accent-primary)' }} />
              <span>Personal Learning Snapshot</span>
            </h2>

            {snapshotLoading ? (
              <LoadingState message="Calculating real activity metrics…" />
            ) : snapshotError ? (
              <div style={{ fontSize: 12.5, color: 'var(--text-muted)' }}>
                {snapshotError}
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
                <div
                  style={{
                    background: 'rgba(0, 0, 0, 0.25)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 12,
                    padding: '12px 14px',
                    textAlign: 'center',
                  }}
                >
                  <FileCode size={18} style={{ color: '#a5b4fc', margin: '0 auto 4px' }} />
                  <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)' }}>
                    {totalSubmissions}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>
                    Submissions
                  </div>
                </div>

                <div
                  style={{
                    background: 'rgba(0, 0, 0, 0.25)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 12,
                    padding: '12px 14px',
                    textAlign: 'center',
                  }}
                >
                  <Target size={18} style={{ color: '#fbbf24', margin: '0 auto 4px' }} />
                  <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)' }}>
                    {conceptsPracticed}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>
                    Concepts
                  </div>
                </div>

                <div
                  style={{
                    background: 'rgba(0, 0, 0, 0.25)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 12,
                    padding: '12px 14px',
                    textAlign: 'center',
                  }}
                >
                  <CheckCircle2 size={18} style={{ color: '#10b981', margin: '0 auto 4px' }} />
                  <div style={{ fontSize: 20, fontWeight: 800, color: '#10b981' }}>
                    {comfortableCount}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>
                    Comfortable
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* CURRENT FOCUS & CONTINUE LEARNING CTA */}
          <div
            style={{
              background: 'rgba(99, 102, 241, 0.04)',
              border: '1px solid rgba(99, 102, 241, 0.28)',
              borderRadius: 16,
              padding: '22px 24px',
              display: 'flex',
              flexDirection: 'column',
              gap: 12,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Compass size={18} style={{ color: 'var(--accent-primary)' }} />
              <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
                Current Target Focus
              </h2>
            </div>

            {primaryFocus ? (
              <>
                <div style={{ fontSize: 15, fontWeight: 700, color: '#c7d2fe' }}>
                  {primaryFocus}
                </div>
                {recommendedAction && (
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    👉 {recommendedAction}
                  </div>
                )}
                {rationale && (
                  <div style={{ fontSize: 12.5, color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    <MarkdownRenderer text={rationale} />
                  </div>
                )}
              </>
            ) : (
              <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                Submit code in the Tutor to unlock your personalized learning focus and tailored recommendations.
              </div>
            )}

            <button
              className="btn-primary"
              style={{ marginTop: 4, width: '100%', padding: '10px 18px', fontSize: 13 }}
              onClick={() => navigate('/tutor')}
            >
              <Bot size={16} />
              <span>Continue Learning in Tutor</span>
              <ArrowRight size={15} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
