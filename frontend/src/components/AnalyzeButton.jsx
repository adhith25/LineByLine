import React from 'react';

export default function AnalyzeButton({ onAnalyze, isLoading, persona }) {
  return (
    <button
      className="btn-primary"
      onClick={onAnalyze}
      disabled={isLoading}
    >
      {isLoading ? (
        <>
          <span
            className="spinner"
            style={{
              width: 16,
              height: 16,
              borderWidth: 2,
            }}
          />
          Analyzing Code with Gemini...
        </>
      ) : (
        <>
          <span>⚡</span>
          <span>Analyze & Explain Code</span>
          <span style={{ fontSize: 11, opacity: 0.8, fontWeight: 400, marginLeft: 4 }}>
            ({persona.toUpperCase()})
          </span>
        </>
      )}
    </button>
  );
}
