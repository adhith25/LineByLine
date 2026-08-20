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

  const { rationale, primary_concept, resources } = recommendationData;

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
        }}
      >
        <div className="card-title" style={{ color: '#fbbf24', marginBottom: 0 }}>
          <span>📚</span>
          <span>Verified Learning Resources — {primary_concept}</span>
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
          }}
          title="All links are hand-verified from trusted educational domains."
        >
          ✅ Zero Hallucinated URLs
        </span>
      </div>

      {rationale && (
        <div
          style={{
            fontSize: 12.5,
            color: '#fde68a',
            background: 'rgba(0,0,0,0.22)',
            padding: '10px 14px',
            borderRadius: 10,
            marginBottom: 16,
            border: '1px solid rgba(245,158,11,0.15)',
          }}
        >
          <MarkdownRenderer
            text={rationale}
            style={{ fontSize: 12.5, color: '#fde68a', lineHeight: 1.65 }}
          />
        </div>
      )}

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
