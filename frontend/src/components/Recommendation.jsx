import React from 'react';
import MarkdownRenderer from './MarkdownRenderer';

const TYPE_ICON = {
  official_docs: '📘',
  tutorial: '🎓',
  guide: '📖',
  video_playlist: '🎬',
  exercise: '🏋️',
  search: '🔍',
};

const TYPE_LABEL = {
  official_docs: 'Official Docs',
  tutorial: 'Tutorial',
  guide: 'Deep Guide',
  video_playlist: 'Video Course',
  exercise: 'Practice',
  search: 'Trusted Search',
};

const TYPE_COLOR = {
  official_docs: '#60a5fa',
  tutorial: '#34d399',
  guide: '#a78bfa',
  video_playlist: '#fb923c',
  exercise: '#f472b6',
  search: '#9ca3af',
};

const STATUS_META = {
  mastered: { label: 'Comfortable', icon: '✅', color: '#10b981', bg: 'rgba(16,185,129,0.14)', border: 'rgba(16,185,129,0.4)' },
  weak:     { label: 'Still Learning', icon: '⚠️', color: '#f59e0b', bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.4)' },
  missing:  { label: 'Needs Practice', icon: '🔴', color: '#ef4444', bg: 'rgba(239,68,68,0.10)', border: 'rgba(239,68,68,0.35)' },
};

const PRIO_META = {
  high:   { label: 'High',   color: '#ef4444', bg: 'rgba(239,68,68,0.12)', icon: '🔥' },
  medium: { label: 'Medium', color: '#f59e0b', bg: 'rgba(245,158,11,0.12)', icon: '⚡' },
  low:    { label: 'Low',    color: '#60a5fa', bg: 'rgba(96,165,250,0.12)', icon: '💧' },
};

function masteryBar(score, status) {
  const s = Math.max(0, Math.min(1, typeof score === 'number' ? score : 0));
  const meta = STATUS_META[status] || STATUS_META.missing;
  return (
    <div
      style={{
        width: '100%',
        height: 6,
        background: 'rgba(255,255,255,0.08)',
        borderRadius: 3,
        overflow: 'hidden',
        marginTop: 6,
      }}
    >
      <div
        style={{
          height: '100%',
          width: `${Math.round(s * 100)}%`,
          background: meta.color,
          transition: 'width 0.3s ease',
        }}
      />
    </div>
  );
}

function PrerequisiteChain({ chain }) {
  if (!chain || !Array.isArray(chain) || chain.length === 0) return null;
  const items = chain.slice(0, 6);

  return (
    <div style={{ marginBottom: 16 }}>
      <div
        style={{
          fontSize: 12,
          color: '#fbbf24',
          fontWeight: 700,
          marginBottom: 8,
          letterSpacing: 0.3,
          textTransform: 'uppercase',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
        }}
      >
        <span>🧭</span>
        <span>Learning Path — What You Need First</span>
      </div>

      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 6,
        }}
      >
        {items.map((item, idx) => {
          const meta = STATUS_META[item.status] || STATUS_META.missing;
          const isLast = idx === items.length - 1;
          return (
            <React.Fragment key={idx}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 10,
                  padding: '10px 12px',
                  background: isLast ? 'rgba(245,158,11,0.09)' : meta.bg,
                  border: `1px solid ${isLast ? 'rgba(245,158,11,0.35)' : meta.border}`,
                  borderRadius: 10,
                }}
              >
                <div
                  style={{
                    width: 22,
                    height: 22,
                    borderRadius: '50%',
                    background: meta.color,
                    color: '#0b0f19',
                    fontSize: 11,
                    fontWeight: 900,
                    flexShrink: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {idx + 1}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: 8,
                      marginBottom: 2,
                    }}
                  >
                    <div
                      style={{
                        fontSize: 13,
                        fontWeight: 700,
                        color: isLast ? '#fde68a' : '#f1f5f9',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6,
                      }}
                    >
                      {isLast && <span style={{ fontSize: 12 }}>🎯</span>}
                      <span>{item.concept}</span>
                    </div>
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 700,
                        padding: '2px 7px',
                        borderRadius: 8,
                        background: meta.bg,
                        color: meta.color,
                        border: `1px solid ${meta.border}`,
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {meta.icon} {meta.label}
                    </span>
                  </div>
                  {item.why && (
                    <div
                      style={{
                        fontSize: 11.5,
                        color: '#cbd5e1',
                        lineHeight: 1.5,
                        marginBottom: 2,
                      }}
                    >
                      {item.why}
                    </div>
                  )}
                  {masteryBar(item.mastery_score, item.status)}
                  <div
                    style={{
                      fontSize: 10,
                      color: 'var(--text-muted)',
                      marginTop: 4,
                      textAlign: 'right',
                    }}
                  >
                    {Math.round((item.mastery_score || 0) * 100)}% mastery
                  </div>
                </div>
              </div>
              {!isLast && (
                <div
                  style={{
                    alignSelf: 'center',
                    fontSize: 14,
                    color: 'rgba(245,158,11,0.45)',
                    lineHeight: 1,
                  }}
                >
                  ↓
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

function NextSteps({ steps }) {
  if (!steps || !Array.isArray(steps) || steps.length === 0) return null;

  return (
    <div style={{ marginBottom: 16 }}>
      <div
        style={{
          fontSize: 12,
          color: '#fbbf24',
          fontWeight: 700,
          marginBottom: 8,
          letterSpacing: 0.3,
          textTransform: 'uppercase',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
        }}
      >
        <span>🎯</span>
        <span>Your Next Steps</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {steps.map((s, i) => {
          const prio = PRIO_META[s.priority] || PRIO_META.medium;
          return (
            <div
              key={i}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 10,
                padding: '9px 12px',
                background: 'rgba(0,0,0,0.25)',
                border: '1px solid var(--border-color)',
                borderRadius: 10,
              }}
            >
              <span style={{ fontSize: 14, flexShrink: 0, marginTop: 1 }}>
                {prio.icon}
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    fontSize: 12.5,
                    color: '#f1f5f9',
                    lineHeight: 1.5,
                    fontWeight: 500,
                  }}
                >
                  {s.action}
                </div>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    marginTop: 6,
                    flexWrap: 'wrap',
                    fontSize: 10.5,
                  }}
                >
                  <span
                    style={{
                      background: prio.bg,
                      color: prio.color,
                      padding: '1px 6px',
                      borderRadius: 5,
                      fontWeight: 700,
                      border: `1px solid ${prio.color}33`,
                    }}
                  >
                    {prio.label}
                  </span>
                  {s.estimated_minutes && (
                    <span style={{ color: 'var(--text-muted)' }}>
                      ⏱ ~{s.estimated_minutes} min
                    </span>
                  )}
                  {s.concept && (
                    <span
                      style={{
                        color: '#a5b4fc',
                        background: 'rgba(99,102,241,0.10)',
                        padding: '1px 6px',
                        borderRadius: 5,
                        border: '1px solid rgba(99,102,241,0.25)',
                      }}
                    >
                      {s.concept}
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function Recommendation({ recommendationData, isLoading }) {
  if (isLoading) {
    return (
      <div
        className="card-box"
        style={{
          border: '1px solid rgba(245, 158, 11, 0.3)',
          background: 'rgba(245, 158, 11, 0.04)',
        }}
      >
        <div className="card-title" style={{ color: '#fbbf24' }}>
          <span>📚</span>
          <span>Learning Recommendations</span>
        </div>
        <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>
          Fetching verified resources...
        </div>
      </div>
    );
  }

  if (!recommendationData || !recommendationData.resources || recommendationData.resources.length === 0) {
    return (
      <div
        className="card-box"
        style={{
          border: '1px solid rgba(245, 158, 11, 0.2)',
          background: 'rgba(245, 158, 11, 0.03)',
        }}
      >
        <div className="card-title" style={{ color: '#fbbf24' }}>
          <span>📚</span>
          <span>Learning Recommendations</span>
        </div>
        <div
          style={{
            textAlign: 'center',
            padding: '14px 12px',
            color: 'var(--text-muted)',
            fontSize: 12.5,
            display: 'flex',
            flexDirection: 'column',
            gap: 6,
            alignItems: 'center',
          }}
        >
          <span style={{ fontSize: 24, opacity: 0.6 }}>🔎</span>
          <div style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>
            No recommendations yet
          </div>
          <div style={{ fontSize: 11.5, maxWidth: 320 }}>
            Complete explanations and concept checks to unlock verified learning resources tailored to your struggles.
          </div>
        </div>
      </div>
    );
  }

  const { rationale, primary_concept, resources,
          prerequisite_chain, next_steps,
          recommended_action, guidance_summary, source } = recommendationData;
  const hasGuidance = prerequisite_chain || next_steps || recommended_action || guidance_summary;

  return (
    <div
      className="card-box"
      style={{
        border: '1px solid rgba(245, 158, 11, 0.3)',
        background: 'rgba(245, 158, 11, 0.04)',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 4,
          gap: 8,
          flexWrap: 'wrap',
        }}
      >
        <div className="card-title" style={{ color: '#fbbf24', marginBottom: 0 }}>
          <span>📚</span>
          <span>Learning Plan — {primary_concept}</span>
        </div>
        <span
          style={{
            fontSize: 10,
            background: 'rgba(16, 185, 129, 0.12)',
            color: '#34d399',
            padding: '2px 8px',
            borderRadius: 10,
            fontWeight: 700,
            border: '1px solid rgba(16, 185, 129, 0.3)',
            whiteSpace: 'nowrap',
          }}
          title="All links are hand-verified from trusted educational domains."
        >
          ✅ Zero Hallucinated URLs
        </span>
      </div>

      {/* ─────── Phase 8: Recommended Action (always visible if present) ─────── */}
      {recommended_action && (
        <div
          style={{
            marginTop: 10,
            padding: '10px 14px',
            background: 'rgba(245, 158, 11, 0.10)',
            border: '1px solid rgba(245, 158, 11, 0.35)',
            borderRadius: 10,
            fontSize: 13,
            color: '#fde68a',
            lineHeight: 1.5,
            fontWeight: 600,
            display: 'flex',
            alignItems: 'flex-start',
            gap: 8,
          }}
        >
          <span style={{ fontSize: 14, flexShrink: 0, marginTop: 1 }}>👉</span>
          <div>{recommended_action}</div>
        </div>
      )}

      {rationale && (
        <div
          style={{
            fontSize: 12.5,
            color: '#fde68a',
            background: 'rgba(0,0,0,0.22)',
            padding: '10px 14px',
            borderRadius: 10,
            margin: hasGuidance ? '12px 0 0' : '12px 0 16px',
            border: '1px solid rgba(245,158,11,0.15)',
          }}
        >
          <MarkdownRenderer
            text={rationale}
            style={{ fontSize: 12.5, color: '#fde68a', lineHeight: 1.65 }}
          />
        </div>
      )}

      {/* ─────── Phase 8: Guidance Summary paragraph ─────── */}
      {guidance_summary && (
        <div
          style={{
            fontSize: 12,
            color: '#e2e8f0',
            background: 'rgba(15,23,42,0.5)',
            padding: '10px 14px',
            borderRadius: 10,
            margin: '12px 0 0',
            border: '1px solid rgba(203,213,225,0.14)',
            lineHeight: 1.65,
          }}
        >
          <MarkdownRenderer
            text={guidance_summary}
            style={{ fontSize: 12, color: '#e2e8f0', lineHeight: 1.65 }}
          />
          {source && source === 'rule_based_fallback' && (
            <div
              style={{
                marginTop: 8,
                fontSize: 10.5,
                color: 'var(--text-muted)',
                fontStyle: 'italic',
              }}
            >
              💡 Tip: When an AI analysis is available, this plan becomes even more tailored to you.
            </div>
          )}
        </div>
      )}

      {/* ─────── Phase 8: Prerequisite Chain + Next Steps ─────── */}
      {hasGuidance && (
        <div style={{ marginTop: 16 }}>
          <PrerequisiteChain chain={prerequisite_chain} />
          <NextSteps steps={next_steps} />
          <div
            style={{
              fontSize: 11,
              color: 'var(--text-muted)',
              textAlign: 'center',
              margin: '-4px 0 12px',
              fontStyle: 'italic',
            }}
          >
            ⤷ Prerequisites identified dynamically per request. No static prerequisite graph stored.
          </div>
        </div>
      )}

      {/* ─────── Phase 5: Verified Resources (always shown) ─────── */}
      <div
        style={{
          fontSize: 12,
          color: '#fbbf24',
          fontWeight: 700,
          marginBottom: 8,
          letterSpacing: 0.3,
          textTransform: 'uppercase',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
        }}
      >
        <span>📖</span>
        <span>Verified Resources</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {resources.map((r, idx) => (
          <a
            key={idx}
            href={r.url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'block',
              textDecoration: 'none',
              background: 'rgba(0, 0, 0, 0.28)',
              border: '1px solid var(--border-color)',
              borderRadius: 10,
              padding: '10px 14px',
              transition: 'all 0.18s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor =
                'rgba(245, 158, 11, 0.5)';
              e.currentTarget.style.background =
                'rgba(245, 158, 11, 0.06)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor =
                'var(--border-color)';
              e.currentTarget.style.background =
                'rgba(0, 0, 0, 0.28)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
              <span style={{ fontSize: 14 }}>{TYPE_ICON[r.type] || '🔗'}</span>
              <span
                style={{
                  fontSize: 13.5,
                  fontWeight: 600,
                  color: '#fef3c7',
                }}
              >
                {r.title}
              </span>
            </div>

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                flexWrap: 'wrap',
                fontSize: 11.5,
                marginLeft: 22,
              }}
            >
              <span
                style={{
                  background: `${TYPE_COLOR[r.type] || '#6b7280'}22`,
                  color: TYPE_COLOR[r.type] || '#d1d5db',
                  padding: '1px 6px',
                  borderRadius: 4,
                  fontWeight: 600,
                }}
              >
                {TYPE_LABEL[r.type] || 'Resource'}
              </span>
              <span style={{ color: 'var(--text-muted)' }}>
                🌐 {r.source}
              </span>
              {r.category && (
                <span
                  style={{
                    background: 'rgba(99, 102, 241, 0.12)',
                    color: '#a5b4fc',
                    padding: '1px 6px',
                    borderRadius: 4,
                    fontWeight: 500,
                  }}
                >
                  {r.category}
                </span>
              )}
            </div>
          </a>
        ))}
      </div>

      <div
        style={{
          marginTop: 12,
          fontSize: 11,
          color: 'var(--text-muted)',
          textAlign: 'center',
          fontStyle: 'italic',
        }}
      >
        Resources are curated from Python docs, MDN, GeeksforGeeks, freeCodeCamp &amp; more.
      </div>
    </div>
  );
}
