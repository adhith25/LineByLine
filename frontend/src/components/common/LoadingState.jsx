import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingState({ message = 'Loading…', fullHeight = false }) {
  return (
    <div
      className={`loading-state-page${fullHeight ? ' full-height' : ''}`}
      role="status"
      aria-live="polite"
    >
      <Loader2
        size={28}
        style={{
          color: 'var(--accent-primary)',
          animation: 'spin 0.8s linear infinite',
        }}
        aria-hidden="true"
      />
      <p className="loading-state-text">{message}</p>
    </div>
  );
}
