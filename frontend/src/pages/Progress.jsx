import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { fetchProgress, fetchRecommendations } from '../services/api';
import LoadingState from '../components/common/LoadingState';
import EmptyState from '../components/common/EmptyState';
import MasteryBar, { MasteryStatusBadge, getMasteryCategory } from '../components/learning/MasteryBar';
import MarkdownRenderer from '../components/MarkdownRenderer';
import {
  Sparkles,
  Bot,
  TrendingUp,
  Target,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  BookOpen,
  ArrowRight,
  Compass,
  AlertCircle,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Flame,
} from 'lucide-react';

const RESOURCE_TYPE_LABEL = {
  official_docs: 'Official Docs',
  tutorial: 'Tutorial',
  guide: 'Deep Guide',
  video_playlist: 'Video Course',
  exercise: 'Practice',
  search: 'Trusted Search',
};

const RESOURCE_TYPE_COLOR = {
  official_docs: '#60a5fa',
  tutorial: '#34d399',
  guide: '#a78bfa',
  video_playlist: '#fb923c',
  exercise: '#f472b6',
  search: '#9ca3af',
};

export default function Progress() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [mounted, setMounted] = useState(false);

  const [progressData, setProgressData] = useState(null);
  const [recData, setRecData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [expandedConcepts, setExpandedConcepts] = useState({});

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [prog, rec] = await Promise.allSettled([
        fetchProgress(),
        fetchRecommendations(),
      ]);

      if (prog.status === 'fulfilled') {
        setProgressData(prog.value);
      } else {
        console.warn('[Progress] fetchProgress failed:', prog.reason);
      }

      if (rec.status === 'fulfilled') {
        setRecData(rec.value);
      } else {
        console.warn('[Progress] fetchRecommendations failed:', rec.reason);
      }

      if (prog.status === 'rejected' && rec.status === 'rejected') {
        setError(prog.reason?.message || 'Failed to load progress data. Please try again.');
      }
    } catch (err) {
      setError(err?.message || 'An unexpected error occurred while loading progress.');
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
      loadData();
    }
  }, [authLoading, user, loadData]);

  const toggleExpand = (conceptId) => {
    setExpandedConcepts((prev) => ({
      ...prev,
      [conceptId]: !prev[conceptId],
    }));
  };

  if (authLoading || (loading && !progressData && !recData && !error)) {
    return <LoadingState message="Loading your progress dashboard…" fullHeight />;
  }

  if (error && !progressData && !recData) {
    return (
      <div className={`page-container${mounted ? ' page-in' : ''}`}>
        <header className="page-header">
          <div>
            <div className="page-kicker">
              <Sparkles size={14} aria-hidden="true" />
              <span>Learning Dashboard</span>
            </div>
            <h1 className="page-title">Your Learning Progress</h1>
            <p className="page-subtitle">Track your Python mastery, identify gaps, and see your growth.</p>
          </div>
        </header>
        <div className="error-banner" style={{ marginTop: 24 }} role="alert">
          <AlertCircle size={18} aria-hidden="true" />
          <div style={{ flex: 1, fontSize: 13.5 }}>{error}</div>
          <button className="btn-secondary" style={{ marginLeft: 'auto' }} onClick={loadData}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const masteryList = progressData?.mastery || [];

  // Summary counts
  const totalPracticed = masteryList.length;
  let comfortableCount = 0;
  let learningCount = 0;
  let needsPracticeCount = 0;

  masteryList.forEach((m) => {
    const cat = getMasteryCategory(m.mastery_score);
    if (cat === 'comfortable') comfortableCount++;
    else if (cat === 'learning') learningCount++;
    else needsPracticeCount++;
  });

  // Sort mastery list:
  // 1. Needs Practice (< 0.25)
  // 2. Still Learning (0.25..0.75)
  // 3. Comfortable (>= 0.75)
  // Within each category: lowest mastery score first
  const sortedMastery = [...masteryList].sort((a, b) => {
    const catA = getMasteryCategory(a.mastery_score);
    const catB = getMasteryCategory(b.mastery_score);
    const order = { needs_practice: 1, learning: 2, comfortable: 3 };
    if (order[catA] !== order[catB]) {
      return order[catA] - order[catB];
    }
    return (a.mastery_score || 0) - (b.mastery_score || 0);
  });

  const primaryConcept = recData?.primary_concept;
  const rationale = recData?.rationale;
  const recommendedAction = recData?.recommended_action;
  const guidanceSummary = recData?.guidance_summary;
  const prereqChain = recData?.prerequisite_chain || [];
  const nextSteps = recData?.next_steps || [];
  const resources = recData?.resources || [];

  return (
    <div className={`page-container${mounted ? ' page-in' : ''}`}>
      {/* 1. PAGE HEADER */}
      <header className="page-header">
        <div>
          <div className="page-kicker">
            <Sparkles size={14} aria-hidden="true" />
            <span>Learning Dashboard</span>
          </div>
          <h1 className="page-title">Your Learning Progress</h1>
          <p className="page-subtitle">
            Understand your current python skill, focus areas, and recommended next steps based on real activity.
          </p>
        </div>
      </header>

      {/* 2. LEARNING OVERVIEW */}
      {totalPracticed === 0 ? (
        <EmptyState
          icon={<Sparkles size={40} style={{ opacity: 0.55 }} />}
          title="No learning activity yet"
          description="Submit code snippets in the Tutor to start building your concept mastery profile and personalized guidance."
          action={<Bot size={16} aria-hidden="true" />}
          actionLabel="Start Learning"
          onAction={() => navigate('/tutor')}
        />
      ) : (
        <>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: 14,
            }}
          >
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: 14,
                padding: '16px 18px',
              }}
            >
              <div style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                Concepts Practiced
              </div>
              <div style={{ fontSize: 28, fontWeight: 800, color: 'var(--text-primary)', marginTop: 4 }}>
                {totalPracticed}
              </div>
            </div>

            <div
              style={{
                background: 'rgba(16, 185, 129, 0.05)',
                border: '1px solid rgba(16, 185, 129, 0.25)',
                borderRadius: 14,
                padding: '16px 18px',
              }}
            >
              <div style={{ fontSize: 12, color: '#34d399', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, display: 'flex', alignItems: 'center', gap: 6 }}>
                <CheckCircle2 size={14} />
                <span>Comfortable</span>
              </div>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#10b981', marginTop: 4 }}>
                {comfortableCount}
              </div>
            </div>

            <div
              style={{
                background: 'rgba(245, 158, 11, 0.05)',
                border: '1px solid rgba(245, 158, 11, 0.25)',
                borderRadius: 14,
                padding: '16px 18px',
              }}
            >
              <div style={{ fontSize: 12, color: '#fbbf24', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, display: 'flex', alignItems: 'center', gap: 6 }}>
                <TrendingUp size={14} />
                <span>Still Learning</span>
              </div>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#f59e0b', marginTop: 4 }}>
                {learningCount}
              </div>
            </div>

            <div
              style={{
                background: 'rgba(239, 68, 68, 0.05)',
                border: '1px solid rgba(239, 68, 68, 0.25)',
                borderRadius: 14,
                padding: '16px 18px',
              }}
            >
              <div style={{ fontSize: 12, color: '#fca5a5', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, display: 'flex', alignItems: 'center', gap: 6 }}>
                <AlertTriangle size={14} />
                <span>Needs Practice</span>
              </div>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#ef4444', marginTop: 4 }}>
                {needsPracticeCount}
              </div>
            </div>
          </div>

          {/* 3. CONCEPT MASTERY VISUALIZATION */}
          <section style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Target size={18} style={{ color: 'var(--accent-primary)' }} />
              <span>Concept Mastery</span>
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {sortedMastery.map((m) => {
                const conceptKey = m.concept_id || m.concept_name;
                const isExpanded = !!expandedConcepts[conceptKey];
                const pct = Math.round((m.mastery_score || 0) * 100);

                return (
                  <div
                    key={conceptKey}
                    style={{
                      background: 'var(--bg-card)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 12,
                      padding: '14px 16px',
                      transition: 'border-color 0.2s ease',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
                      <div style={{ flex: 1, minWidth: 160 }}>
                        <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>
                          {m.concept_name || 'Concept'}
                        </div>
                        <MasteryBar score={m.mastery_score} height={7} />
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', minWidth: 40, textAlign: 'right' }}>
                          {pct}%
                        </span>
                        <MasteryStatusBadge score={m.mastery_score} />
                        <button
                          onClick={() => toggleExpand(conceptKey)}
                          style={{
                            background: 'rgba(255,255,255,0.05)',
                            border: '1px solid var(--border-color)',
                            borderRadius: 6,
                            padding: '4px 8px',
                            color: 'var(--text-secondary)',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 4,
                            fontSize: 12,
                          }}
                          aria-expanded={isExpanded}
                          aria-label={`Toggle details for ${m.concept_name}`}
                        >
                          <span>{isExpanded ? 'Less' : 'Details'}</span>
                          {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                        </button>
                      </div>
                    </div>

                    {isExpanded && (
                      <div
                        style={{
                          marginTop: 12,
                          paddingTop: 12,
                          borderTop: '1px solid var(--border-color)',
                          display: 'grid',
                          gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                          gap: 10,
                          fontSize: 12,
                          color: 'var(--text-secondary)',
                        }}
                      >
                        <div>
                          <span style={{ color: 'var(--text-muted)' }}>Attempts: </span>
                          <strong style={{ color: 'var(--text-primary)' }}>{m.attempts}</strong>
                        </div>
                        <div>
                          <span style={{ color: 'var(--text-muted)' }}>Correct: </span>
                          <strong style={{ color: '#10b981' }}>{m.correct_count}</strong>
                        </div>
                        <div>
                          <span style={{ color: 'var(--text-muted)' }}>Incorrect: </span>
                          <strong style={{ color: '#ef4444' }}>{m.incorrect_count}</strong>
                        </div>
                        <div>
                          <span style={{ color: 'var(--text-muted)' }}>Struggles: </span>
                          <strong style={{ color: '#f59e0b' }}>{m.struggle_count}</strong>
                        </div>
                        {m.last_activity_at && (
                          <div style={{ gridColumn: '1 / -1' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Last Practice: </span>
                            <span style={{ color: 'var(--text-primary)' }}>
                              {new Date(m.last_activity_at).toLocaleDateString(undefined, {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </section>
        </>
      )}

      {/* 4. RECOMMENDED NEXT STEP */}
      {(recommendedAction || primaryConcept || rationale) && (
        <section
          style={{
            background: 'rgba(99, 102, 241, 0.04)',
            border: '1px solid rgba(99, 102, 241, 0.28)',
            borderRadius: 16,
            padding: '20px 22px',
            display: 'flex',
            flexDirection: 'column',
            gap: 14,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Compass size={20} style={{ color: 'var(--accent-primary)' }} />
              <h2 style={{ fontSize: 17, fontWeight: 700, color: 'var(--text-primary)' }}>
                Recommended Next Focus {primaryConcept ? `— ${primaryConcept}` : ''}
              </h2>
            </div>
            <button
              className="btn-primary"
              style={{ width: 'auto', padding: '8px 18px', fontSize: 13 }}
              onClick={() => navigate('/tutor')}
            >
              <Bot size={15} />
              <span>Continue Learning</span>
              <ArrowRight size={14} />
            </button>
          </div>

          {recommendedAction && (
            <div
              style={{
                background: 'rgba(99, 102, 241, 0.12)',
                border: '1px solid rgba(99, 102, 241, 0.35)',
                borderRadius: 10,
                padding: '12px 14px',
                fontSize: 14,
                fontWeight: 600,
                color: '#e0e7ff',
                display: 'flex',
                alignItems: 'flex-start',
                gap: 8,
              }}
            >
              <span style={{ fontSize: 16 }}>👉</span>
              <div>{recommendedAction}</div>
            </div>
          )}

          {rationale && (
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              <MarkdownRenderer text={rationale} />
            </div>
          )}

          {guidanceSummary && (
            <div
              style={{
                fontSize: 12.5,
                color: 'var(--text-primary)',
                background: 'rgba(0, 0, 0, 0.2)',
                padding: '10px 14px',
                borderRadius: 10,
                border: '1px solid var(--border-color)',
              }}
            >
              <MarkdownRenderer text={guidanceSummary} />
            </div>
          )}
        </section>
      )}

      {/* 5. LEARNING PATH */}
      {prereqChain.length > 0 && (
        <section
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: 16,
            padding: '20px 22px',
          }}
        >
          <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>🧭</span>
            <span>Learning Path — Recommended Sequence</span>
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {prereqChain.map((item, idx) => {
              const isLast = idx === prereqChain.length - 1;
              const cat = item.status ? (item.status === 'mastered' ? 'comfortable' : item.status === 'weak' ? 'learning' : 'needs_practice') : 'learning';

              return (
                <React.Fragment key={idx}>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 12,
                      padding: '12px 14px',
                      background: isLast ? 'rgba(99, 102, 241, 0.08)' : 'rgba(0, 0, 0, 0.2)',
                      border: `1px solid ${isLast ? 'rgba(99, 102, 241, 0.35)' : 'var(--border-color)'}`,
                      borderRadius: 12,
                    }}
                  >
                    <div
                      style={{
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        background: isLast ? 'var(--accent-primary)' : 'rgba(255,255,255,0.1)',
                        color: isLast ? '#fff' : 'var(--text-secondary)',
                        fontSize: 12,
                        fontWeight: 800,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}
                    >
                      {idx + 1}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8, marginBottom: 2 }}>
                        <span style={{ fontSize: 14, fontWeight: 700, color: isLast ? '#c7d2fe' : 'var(--text-primary)' }}>
                          {item.concept}
                        </span>
                        <MasteryStatusBadge score={item.mastery_score || (cat === 'comfortable' ? 0.8 : cat === 'learning' ? 0.5 : 0.1)} />
                      </div>
                      {item.why && (
                        <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: '4px 0 0' }}>
                          {item.why}
                        </p>
                      )}
                    </div>
                  </div>
                  {!isLast && (
                    <div style={{ alignSelf: 'center', color: 'var(--text-muted)', fontSize: 16 }}>↓</div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </section>
      )}

      {/* 6. NEXT STEPS */}
      {nextSteps.length > 0 && (
        <section
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: 16,
            padding: '20px 22px',
          }}
        >
          <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Flame size={18} style={{ color: '#f59e0b' }} />
            <span>Actionable Next Tasks</span>
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {nextSteps.map((step, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 12,
                  padding: '10px 14px',
                  background: 'rgba(0, 0, 0, 0.2)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 10,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1, minWidth: 0 }}>
                  <span style={{ fontSize: 13, color: 'var(--accent-primary)' }}>•</span>
                  <span style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 500 }}>
                    {step.action}
                  </span>
                </div>
                {step.estimated_minutes && (
                  <span style={{ fontSize: 11, color: 'var(--text-muted)', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Clock size={12} />
                    <span>~{step.estimated_minutes} min</span>
                  </span>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 7. LEARNING RESOURCES */}
      <section
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: 16,
          padding: '20px 22px',
        }}
      >
        <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
          <BookOpen size={18} style={{ color: '#60a5fa' }} />
          <span>Verified Learning Resources</span>
        </h2>

        {resources.length === 0 ? (
          <div style={{ fontSize: 13, color: 'var(--text-muted)', textAlign: 'center', padding: '16px 0' }}>
            No resources available yet. Complete more tutor exercises to generate tailored material.
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 10 }}>
            {resources.map((res, idx) => (
              <a
                key={idx}
                href={res.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 6,
                  padding: '12px 14px',
                  background: 'rgba(0, 0, 0, 0.25)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 10,
                  textDecoration: 'none',
                  transition: 'border-color 0.18s ease, background 0.18s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.4)';
                  e.currentTarget.style.background = 'rgba(99, 102, 241, 0.06)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-color)';
                  e.currentTarget.style.background = 'rgba(0, 0, 0, 0.25)';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                  <span style={{ fontSize: 13.5, fontWeight: 700, color: '#f1f5f9', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {res.title}
                  </span>
                  <ExternalLink size={13} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap', fontSize: 11 }}>
                  <span
                    style={{
                      background: `${RESOURCE_TYPE_COLOR[res.type] || '#6b7280'}22`,
                      color: RESOURCE_TYPE_COLOR[res.type] || '#d1d5db',
                      padding: '1px 6px',
                      borderRadius: 4,
                      fontWeight: 600,
                    }}
                  >
                    {RESOURCE_TYPE_LABEL[res.type] || 'Resource'}
                  </span>
                  <span style={{ color: 'var(--text-muted)' }}>🌐 {res.source}</span>
                </div>
              </a>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
