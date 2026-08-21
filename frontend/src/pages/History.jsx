import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { fetchSubmissions, fetchSubmissionDetail } from '../services/api';
import LoadingState from '../components/common/LoadingState';
import EmptyState from '../components/common/EmptyState';
import MarkdownRenderer from '../components/MarkdownRenderer';
import {
  History as HistoryIcon,
  Bot,
  Code2,
  Copy,
  Check,
  ChevronRight,
  ChevronDown,
  AlertCircle,
  Clock,
  Sparkles,
  HelpCircle,
  X,
  FileCode,
  Tag,
} from 'lucide-react';

export default function History() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [mounted, setMounted] = useState(false);

  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Selected submission for detail view (expanded id)
  const [expandedId, setExpandedId] = useState(null);
  const [detailData, setDetailData] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const [copiedId, setCopiedId] = useState(null);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSubmissions(50);
      setSubmissions(data?.submissions || []);
    } catch (err) {
      console.error('[History] Failed to load submissions:', err);
      setError(err?.message || 'Failed to load submission history.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const t = setTimeout(() => setMounted(true), 30);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    if (!authLoading && user) {
      loadHistory();
    }
  }, [authLoading, user, loadHistory]);

  const handleSelectSubmission = async (sub) => {
    if (expandedId === sub.id) {
      setExpandedId(null);
      setDetailData(null);
      return;
    }

    setExpandedId(sub.id);
    setDetailData(sub); // optimistic initial data from list
    setDetailLoading(true);

    try {
      const detail = await fetchSubmissionDetail(sub.id);
      if (detail) {
        setDetailData(detail);
      }
    } catch (err) {
      console.warn('[History] Detail fetch failed, fallback to list item:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleCopyCode = async (codeStr, id, e) => {
    e.stopPropagation();
    if (!codeStr) return;
    try {
      await navigator.clipboard.writeText(codeStr);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error('[History] Copy code failed:', err);
    }
  };

  if (authLoading || (loading && submissions.length === 0 && !error)) {
    return <LoadingState message="Loading your submission history…" fullHeight />;
  }

  return (
    <div className={`page-container${mounted ? ' page-in' : ''}`}>
      {/* HEADER */}
      <header className="page-header">
        <div>
          <div className="page-kicker">
            <HistoryIcon size={14} aria-hidden="true" />
            <span>Submissions</span>
          </div>
          <h1 className="page-title">Learning History</h1>
          <p className="page-subtitle">
            Review past code explorations, misconception insights, and concept checks.
          </p>
        </div>
      </header>

      {/* ERROR STATE */}
      {error && (
        <div className="error-banner" role="alert">
          <AlertCircle size={18} aria-hidden="true" />
          <div style={{ flex: 1, fontSize: 13.5 }}>{error}</div>
          <button className="btn-secondary" style={{ marginLeft: 'auto' }} onClick={loadHistory}>
            Retry
          </button>
        </div>
      )}

      {/* EMPTY STATE */}
      {!loading && submissions.length === 0 && !error ? (
        <EmptyState
          icon={<HistoryIcon size={40} style={{ opacity: 0.55 }} />}
          title="No learning sessions yet"
          description="Your code submissions, AI explanations, and concept checks will be saved here automatically."
          action={<Bot size={16} aria-hidden="true" />}
          actionLabel="Start Learning"
          onAction={() => navigate('/tutor')}
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {submissions.map((sub) => {
            const isExpanded = expandedId === sub.id;
            const formattedDate = sub.created_at
              ? new Date(sub.created_at).toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })
              : 'Recent';

            const activeDetail = isExpanded ? detailData || sub : sub;

            return (
              <div
                key={sub.id}
                style={{
                  background: 'var(--bg-card)',
                  border: `1px solid ${isExpanded ? 'rgba(99, 102, 241, 0.4)' : 'var(--border-color)'}`,
                  borderRadius: 14,
                  overflow: 'hidden',
                  transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
                  boxShadow: isExpanded ? '0 4px 20px rgba(0, 0, 0, 0.25)' : 'none',
                }}
              >
                {/* CARD SUMMARY ROW */}
                <div
                  onClick={() => handleSelectSubmission(sub)}
                  style={{
                    padding: '16px 18px',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 10,
                  }}
                  role="button"
                  tabIndex={0}
                  aria-expanded={isExpanded}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handleSelectSubmission(sub);
                    }
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                      <span
                        style={{
                          background: 'rgba(99, 102, 241, 0.12)',
                          color: '#a5b4fc',
                          border: '1px solid rgba(99, 102, 241, 0.3)',
                          fontSize: 11,
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: 6,
                          textTransform: 'uppercase',
                        }}
                      >
                        {sub.language || 'python'}
                      </span>
                      <span
                        style={{
                          background: 'rgba(255, 255, 255, 0.05)',
                          color: 'var(--text-secondary)',
                          border: '1px solid var(--border-color)',
                          fontSize: 11,
                          fontWeight: 600,
                          padding: '2px 8px',
                          borderRadius: 6,
                          textTransform: 'capitalize',
                        }}
                      >
                        {sub.persona || 'beginner'}
                      </span>
                      {sub.has_quiz && (
                        <span
                          style={{
                            background: 'rgba(16, 185, 129, 0.10)',
                            color: '#34d399',
                            border: '1px solid rgba(16, 185, 129, 0.3)',
                            fontSize: 11,
                            fontWeight: 600,
                            padding: '2px 8px',
                            borderRadius: 6,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 4,
                          }}
                        >
                          <Check size={12} />
                          <span>Quiz</span>
                        </span>
                      )}
                      {sub.misconception_summary && (
                        <span
                          style={{
                            background: 'rgba(245, 158, 11, 0.10)',
                            color: '#fbbf24',
                            border: '1px solid rgba(245, 158, 11, 0.3)',
                            fontSize: 11,
                            fontWeight: 600,
                            padding: '2px 8px',
                            borderRadius: 6,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 4,
                          }}
                        >
                          <Sparkles size={12} />
                          <span>Insight</span>
                        </span>
                      )}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ fontSize: 12, color: 'var(--text-muted)', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                        <Clock size={13} />
                        <span>{formattedDate}</span>
                      </span>
                      <button
                        className="btn-secondary"
                        style={{ padding: '4px 10px', fontSize: 12, width: 'auto' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectSubmission(sub);
                        }}
                      >
                        <span>{isExpanded ? 'Collapse' : 'Inspect'}</span>
                        {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                      </button>
                    </div>
                  </div>

                  {/* CODE PREVIEW BLOCK */}
                  <div
                    style={{
                      background: 'rgba(0, 0, 0, 0.3)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 8,
                      padding: '10px 12px',
                      fontFamily: 'var(--font-mono)',
                      fontSize: 12.5,
                      color: '#cbd5e1',
                      overflowX: 'auto',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      lineHeight: 1.45,
                    }}
                  >
                    {sub.code_preview || sub.code || '# Code snippet'}
                  </div>

                  {/* ANALYSIS SUMMARY OR CONCEPTS */}
                  {sub.analysis_summary && (
                    <div style={{ fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                      {sub.analysis_summary}
                    </div>
                  )}

                  {sub.concepts && sub.concepts.length > 0 && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                      <Tag size={12} style={{ color: 'var(--text-muted)' }} />
                      {sub.concepts.map((conceptName, cIdx) => (
                        <span
                          key={cIdx}
                          style={{
                            fontSize: 11,
                            color: '#a5b4fc',
                            background: 'rgba(99, 102, 241, 0.08)',
                            padding: '2px 7px',
                            borderRadius: 4,
                            border: '1px solid rgba(99, 102, 241, 0.2)',
                          }}
                        >
                          {conceptName}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* EXPANDED SUBMISSION DETAILS */}
                {isExpanded && (
                  <div
                    style={{
                      borderTop: '1px solid var(--border-color)',
                      background: 'rgba(0, 0, 0, 0.15)',
                      padding: '20px 22px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 18,
                    }}
                  >
                    {detailLoading && !detailData ? (
                      <LoadingState message="Loading full submission details…" />
                    ) : (
                      <>
                        {/* FULL CODE SECTION */}
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                            <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                              <Code2 size={15} style={{ color: 'var(--accent-primary)' }} />
                              <span>Full Code</span>
                            </div>
                            <button
                              className="btn-secondary"
                              style={{ padding: '4px 10px', fontSize: 11.5, width: 'auto' }}
                              onClick={(e) => handleCopyCode(activeDetail.code, sub.id, e)}
                            >
                              {copiedId === sub.id ? (
                                <>
                                  <Check size={13} style={{ color: '#10b981' }} />
                                  <span style={{ color: '#10b981' }}>Copied!</span>
                                </>
                              ) : (
                                <>
                                  <Copy size={13} />
                                  <span>Copy Code</span>
                                </>
                              )}
                            </button>
                          </div>
                          <pre
                            style={{
                              background: '#090d16',
                              border: '1px solid var(--border-color)',
                              borderRadius: 10,
                              padding: '14px 16px',
                              fontFamily: 'var(--font-mono)',
                              fontSize: 13,
                              color: '#e2e8f0',
                              overflowX: 'auto',
                              lineHeight: 1.55,
                            }}
                          >
                            <code>{activeDetail.code}</code>
                          </pre>
                        </div>

                        {/* MISCONCEPTIONS / INSIGHTS */}
                        {activeDetail.misconceptions && activeDetail.misconceptions.length > 0 && (
                          <div
                            style={{
                              background: 'rgba(245, 158, 11, 0.05)',
                              border: '1px solid rgba(245, 158, 11, 0.25)',
                              borderRadius: 12,
                              padding: '14px 16px',
                            }}
                          >
                            <h3 style={{ fontSize: 14, fontWeight: 700, color: '#fbbf24', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
                              <Sparkles size={15} />
                              <span>Detected Misconceptions &amp; Teaching Insights</span>
                            </h3>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                              {activeDetail.misconceptions.map((mc, mcIdx) => (
                                <div key={mcIdx} style={{ fontSize: 13, color: 'var(--text-primary)' }}>
                                  <strong style={{ color: '#fde68a' }}>{mc.title}</strong>
                                  {mc.explanation && (
                                    <p style={{ fontSize: 12.5, color: 'var(--text-secondary)', marginTop: 4, lineHeight: 1.5 }}>
                                      {mc.explanation}
                                    </p>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* CONCEPT CHECKS / QUIZ RESULTS */}
                        {activeDetail.concept_checks && activeDetail.concept_checks.length > 0 && (
                          <div
                            style={{
                              background: 'rgba(16, 185, 129, 0.05)',
                              border: '1px solid rgba(16, 185, 129, 0.25)',
                              borderRadius: 12,
                              padding: '14px 16px',
                            }}
                          >
                            <h3 style={{ fontSize: 14, fontWeight: 700, color: '#34d399', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
                              <HelpCircle size={15} />
                              <span>Concept Check Results</span>
                            </h3>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                              {activeDetail.concept_checks.map((cc, ccIdx) => (
                                <div
                                  key={ccIdx}
                                  style={{
                                    padding: '10px 12px',
                                    background: 'rgba(0, 0, 0, 0.2)',
                                    border: '1px solid var(--border-color)',
                                    borderRadius: 8,
                                    fontSize: 12.5,
                                  }}
                                >
                                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8, marginBottom: 4 }}>
                                    <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                                      {cc.concept_name || 'Concept Check'}
                                    </span>
                                    <span
                                      style={{
                                        fontSize: 11,
                                        fontWeight: 700,
                                        color: cc.is_correct ? '#10b981' : '#ef4444',
                                      }}
                                    >
                                      {cc.is_correct ? 'Correct ✓' : 'Needs Practice ✗'}
                                    </span>
                                  </div>
                                  {cc.question_text && (
                                    <div style={{ color: 'var(--text-secondary)', fontSize: 12 }}>
                                      {cc.question_text}
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
