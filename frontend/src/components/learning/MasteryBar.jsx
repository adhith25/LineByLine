import React from 'react';

export function getMasteryCategory(score) {
  const s = Math.max(0, Math.min(1, typeof score === 'number' ? score : 0));
  if (s >= 0.75) return 'comfortable';
  if (s >= 0.25) return 'learning';
  return 'needs_practice';
}

export const MASTERY_META = {
  comfortable: {
    label: 'Comfortable',
    icon: '✅',
    color: '#10b981',
    bg: 'rgba(16,185,129,0.14)',
    border: 'rgba(16,185,129,0.4)',
  },
  learning: {
    label: 'Still Learning',
    icon: '⚡',
    color: '#f59e0b',
    bg: 'rgba(245,158,11,0.12)',
    border: 'rgba(245,158,11,0.4)',
  },
  needs_practice: {
    label: 'Needs Practice',
    icon: '🎯',
    color: '#ef4444',
    bg: 'rgba(239,68,68,0.10)',
    border: 'rgba(239,68,68,0.35)',
  },
};

export function MasteryStatusBadge({ score }) {
  const cat = getMasteryCategory(score);
  const meta = MASTERY_META[cat];

  return (
    <span
      style={{
        fontSize: 11,
        fontWeight: 700,
        padding: '2px 8px',
        borderRadius: 8,
        background: meta.bg,
        color: meta.color,
        border: `1px solid ${meta.border}`,
        whiteSpace: 'nowrap',
        display: 'inline-flex',
        alignItems: 'center',
        gap: 4,
      }}
    >
      <span>{meta.icon}</span>
      <span>{meta.label}</span>
    </span>
  );
}

export default function MasteryBar({ score, height = 6, animated = true }) {
  const s = Math.max(0, Math.min(1, typeof score === 'number' ? score : 0));
  const cat = getMasteryCategory(s);
  const meta = MASTERY_META[cat];
  const pct = Math.round(s * 100);

  return (
    <div
      style={{
        width: '100%',
        height,
        background: 'rgba(255, 255, 255, 0.08)',
        borderRadius: height / 2,
        overflow: 'hidden',
      }}
      role="progressbar"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`${pct}% mastery`}
    >
      <div
        style={{
          height: '100%',
          width: `${pct}%`,
          background: meta.color,
          transition: animated ? 'width 0.35s ease' : 'none',
          borderRadius: height / 2,
        }}
      />
    </div>
  );
}
