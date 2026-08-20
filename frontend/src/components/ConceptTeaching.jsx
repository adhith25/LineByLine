import React from 'react';
import MarkdownRenderer from './MarkdownRenderer';

function TeachingSkeleton() {
  return (
    <div
      className="card-box concept-teach-card"
      style={{
        border: '1px solid rgba(16, 185, 129, 0.3)',
        background: 'rgba(16, 185, 129, 0.04)',
      }}
    >
      <div className="card-title" style={{ color: '#34d399', marginBottom: 16 }}>
        <span>🎓</span>
        <span>Preparing concept lesson...</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div className="skeleton skeleton-line short" />
        <div className="skeleton skeleton-line" />
        <div className="skeleton skeleton-line medium" />
        <div className="skeleton skeleton-box" />
        <div className="skeleton skeleton-line" />
        <div className="skeleton skeleton-line short" />
      </div>
    </div>
  );
}

export default function ConceptTeaching({ teachingData, isLoading }) {
  if (isLoading) return <TeachingSkeleton />;
  if (!teachingData) return null;

  const {
    concept,
    explanation,
    simple_example,
    connection_to_code,
    common_mistake,
  } = teachingData;

  return (
    <div
      className="card-box concept-teach-card"
      style={{
        border: '1px solid rgba(16, 185, 129, 0.3)',
        background: 'rgba(16, 185, 129, 0.04)',
      }}
    >
      <div className="card-title" style={{ color: '#34d399', marginBottom: 16 }}>
        <span>🎓</span>
        <span>Concept Teaching: {concept || 'Core Concept'}</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
        {/* Deep Explanation */}
        <div className="teach-section">
          <h5 className="teach-heading" style={{ color: '#6ee7b7' }}>
            💡 Understanding the Concept
          </h5>
          <div className="teach-body">
            <MarkdownRenderer
              text={explanation}
              style={{ fontSize: 13.5, color: '#e6f4ea', lineHeight: 1.7 }}
            />
          </div>
        </div>

        {/* Code Example */}
        {simple_example && (
          <div className="teach-section">
            <h5 className="teach-heading" style={{ color: '#6ee7b7' }}>
              ✍️ Simple Working Example
            </h5>
            <pre
              style={{
                background: '#0a0d14',
                padding: '14px 16px',
                borderRadius: 10,
                border: '1px solid rgba(16,185,129,0.2)',
                color: '#6ee7b7',
                fontFamily: 'var(--font-mono)',
                fontSize: 12.5,
                overflowX: 'auto',
                lineHeight: 1.6,
              }}
            >
              <code>{simple_example}</code>
            </pre>
          </div>
        )}

        {/* Connection to student code */}
        {connection_to_code && (
          <div
            className="teach-section"
            style={{
              background: 'rgba(16,185,129,0.07)',
              padding: '12px 14px',
              borderRadius: 10,
              border: '1px solid rgba(16,185,129,0.18)',
            }}
          >
            <h5 className="teach-heading" style={{ color: '#6ee7b7' }}>
              🔗 Connection to Your Code
            </h5>
            <MarkdownRenderer
              text={connection_to_code}
              style={{ fontSize: 13, color: '#d1fae5', lineHeight: 1.65 }}
            />
          </div>
        )}

        {/* Common mistake */}
        {common_mistake && (
          <div
            className="teach-section"
            style={{
              background: 'rgba(239, 68, 68, 0.08)',
              borderLeft: '3px solid #ef4444',
              padding: '12px 14px',
              borderRadius: 8,
            }}
          >
            <h5 className="teach-heading" style={{ color: '#fca5a5' }}>
              ⚠️ Common Mistake to Avoid
            </h5>
            <MarkdownRenderer
              text={common_mistake}
              style={{ fontSize: 13, color: '#fecaca', lineHeight: 1.65 }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
