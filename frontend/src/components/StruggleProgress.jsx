import React from 'react';

export default function StruggleProgress({ struggles, errors }) {
  const struggleEntries = Object.entries(struggles || {});
  const errorEntries = Object.entries(errors || {});

  if (struggleEntries.length === 0 && errorEntries.length === 0) {
    return (
      <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
        No repeated struggles recorded yet. Submit code to track learning progress!
      </p>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {/* Concept-level Misconceptions */}
      {struggleEntries.length > 0 && (
        <div>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
            Concept Struggles
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {struggleEntries.map(([concept, count]) => (
              <div
                key={concept}
                style={{
                  background: 'rgba(245, 158, 11, 0.08)',
                  border: '1px solid rgba(245, 158, 11, 0.25)',
                  padding: '8px 12px',
                  borderRadius: 8,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  fontSize: 13,
                }}
              >
                <span style={{ color: '#fef08a', fontWeight: 500 }}>
                  ⚠️ {concept}
                </span>
                <span
                  style={{
                    background: 'rgba(245, 158, 11, 0.2)',
                    color: '#fbbf24',
                    fontSize: 11,
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: 12,
                  }}
                >
                  {count} {count === 1 ? 'submission' : 'submissions'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Concrete Error Categories */}
      {errorEntries.length > 0 && (
        <div style={{ marginTop: 4 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
            Recurring Code Errors
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {errorEntries.map(([errName, count]) => (
              <div
                key={errName}
                style={{
                  background: 'rgba(239, 68, 68, 0.08)',
                  border: '1px solid rgba(239, 68, 68, 0.25)',
                  padding: '8px 12px',
                  borderRadius: 8,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  fontSize: 13,
                }}
              >
                <span style={{ color: '#fca5a5', fontWeight: 500 }}>
                  🔴 {errName}
                </span>
                <span
                  style={{
                    background: 'rgba(239, 68, 68, 0.2)',
                    color: '#f87171',
                    fontSize: 11,
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: 12,
                  }}
                >
                  {count} {count === 1 ? 'submission' : 'submissions'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
