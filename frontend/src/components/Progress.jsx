import React from 'react';
import StruggleProgress from './StruggleProgress';

function ProgressSkeleton() {
  return (
    <div
      className="card-box"
      style={{
        border: '1px solid rgba(99, 102, 241, 0.3)',
        background: 'rgba(99, 102, 241, 0.04)',
      }}
    >
      <div className="card-title" style={{ color: '#818cf8', marginBottom: 16 }}>
        <span>📊</span>
        <span>Your Learning Progress</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div className="skeleton skeleton-line short" style={{ marginBottom: 6 }} />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
          <div className="skeleton" style={{ height: 44, borderRadius: 10 }} />
          <div className="skeleton" style={{ height: 44, borderRadius: 10 }} />
          <div className="skeleton" style={{ height: 44, borderRadius: 10 }} />
        </div>
        <div className="skeleton skeleton-line short" />
        <div className="skeleton" style={{ height: 60, borderRadius: 10 }} />
      </div>
    </div>
  );
}

function ProgressEmpty() {
  return (
    <div
      className="card-box"
      style={{
        border: '1px solid rgba(99, 102, 241, 0.2)',
        background: 'rgba(99, 102, 241, 0.03)',
      }}
    >
      <div className="card-title" style={{ color: '#818cf8' }}>
        <span>📊</span>
        <span>Your Learning Progress</span>
      </div>
      <div
        style={{
          textAlign: 'center',
          padding: '16px 12px',
          color: 'var(--text-muted)',
          fontSize: 13,
          display: 'flex',
          flexDirection: 'column',
          gap: 6,
          alignItems: 'center',
        }}
      >
        <span style={{ fontSize: 28, opacity: 0.6 }}>🌱</span>
        <div style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>
          No learning data yet
        </div>
        <div style={{ fontSize: 12 }}>
          Submit code and complete concept checks to start tracking your progress!
        </div>
      </div>
    </div>
  );
}

export default function Progress({ progressData, isLoading }) {
  if (isLoading) return <ProgressSkeleton />;
  if (!progressData) return <ProgressEmpty />;

  const { struggles, errors, concept_checks, recent_improvements } = progressData;

  // Aggregate total quiz stats
  let totalAttempts = 0;
  let totalCorrect = 0;
  let totalIncorrect = 0;

  Object.values(concept_checks || {}).forEach((stat) => {
    totalAttempts += stat.attempts || 0;
    totalCorrect += stat.correct || 0;
    totalIncorrect += stat.incorrect || 0;
  });

  return (
    <div
      className="card-box"
      style={{
        border: '1px solid rgba(99, 102, 241, 0.3)',
        background: 'rgba(99, 102, 241, 0.04)',
      }}
    >
      <div className="card-title" style={{ color: '#818cf8' }}>
        <span>📊</span>
        <span>Your Learning Progress</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* Quiz Statistics Bar */}
        {totalAttempts > 0 && (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: 8,
              background: 'rgba(0, 0, 0, 0.25)',
              padding: '10px 14px',
              borderRadius: 10,
              textAlign: 'center',
            }}
          >
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Quiz Attempts</div>
              <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>{totalAttempts}</div>
            </div>
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Correct</div>
              <div style={{ fontSize: 16, fontWeight: 700, color: '#34d399' }}>{totalCorrect}</div>
            </div>
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Incorrect</div>
              <div style={{ fontSize: 16, fontWeight: 700, color: '#fca5a5' }}>{totalIncorrect}</div>
            </div>
          </div>
        )}

        {/* Struggle & Error Tracker */}
        <div>
          <h5 style={{ fontSize: 12, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: 8 }}>
            Repeated Struggles & Errors
          </h5>
          <StruggleProgress struggles={struggles} errors={errors} />
        </div>

        {/* Recent Improvements */}
        {recent_improvements && recent_improvements.length > 0 && (
          <div>
            <h5 style={{ fontSize: 12, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: 8 }}>
              Recent Improvements
            </h5>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {recent_improvements.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'rgba(16, 185, 129, 0.08)',
                    border: '1px solid rgba(16, 185, 129, 0.25)',
                    padding: '8px 12px',
                    borderRadius: 8,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    fontSize: 13,
                    color: '#6ee7b7',
                  }}
                >
                  <span style={{ fontWeight: 800 }}>{item.icon || '✓'}</span>
                  <span>
                    <strong>{item.concept}</strong> — {item.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
