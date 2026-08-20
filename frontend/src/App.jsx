import React from 'react';
import Tutor from './pages/Tutor';
import ErrorBoundary from './components/ErrorBoundary';
import { resetSession } from './services/api';

export default function App() {
  const handleResetSession = async () => {
    try {
      await resetSession();
      window.location.reload();
    } catch (err) {
      console.error('Reset failed:', err);
      alert('Failed to reset session. Please refresh the page manually.');
    }
  };

  return (
    <div>
      <header className="app-header">
        <div className="brand">
          <span className="brand-badge">LBL</span>
          <span className="brand-title">LineByLine</span>
          <span className="brand-subtitle">AI Code Learning Tutor</span>
        </div>

        <div className="header-actions">
          <button className="btn-secondary danger" onClick={handleResetSession}>
            ↺ Reset Session
          </button>
        </div>
      </header>

      <main>
        <ErrorBoundary>
          <Tutor />
        </ErrorBoundary>
      </main>
    </div>
  );
}
