import React from 'react';
import MarkdownRenderer from './MarkdownRenderer';

function LineSkeleton() {
  return (
    <div className="card-box line-breakdown-card">
      <div className="card-title">
        <span>🧩</span>
        <span>Line-by-Line Breakdown</span>
      </div>
      <div className="line-breakdown-list">
        {[0, 1, 2].map((i) => (
          <div key={i} className="line-item-card" style={{ opacity: 0.85 }}>
            <div className="line-item-head">
              <div className="skeleton" style={{ width: 38, height: 22, borderRadius: 6 }} />
              <div className="skeleton" style={{ flex: 1, height: 22, borderRadius: 6 }} />
            </div>
            <div className="skeleton skeleton-line medium" />
            <div className="skeleton skeleton-line" />
          </div>
        ))}
      </div>
    </div>
  );
}

export default function LineExplanation({ lineExplanations, isLoading }) {
  if (isLoading) return <LineSkeleton />;
  if (!lineExplanations || lineExplanations.length === 0) {
    return null;
  }

  return (
    <div className="card-box line-breakdown-card">
      <div className="card-title">
        <span>🧩</span>
        <span>Line-by-Line Breakdown</span>
      </div>

      <div className="line-breakdown-list">
        {lineExplanations.map((item, index) => {
          const lineNum = item.line || item.line_num || index + 1;
          const codeSnippet = item.code || '';
          const noteText = item.note || item.explanation || '';

          return (
            <div key={index} className="line-item-card">
              <div className="line-item-head">
                <div className="line-num-chip">L{lineNum}</div>
                {codeSnippet && (
                  <pre className="line-code-block">
                    <code>{codeSnippet}</code>
                  </pre>
                )}
              </div>
              {noteText && (
                <div className="line-note-body">
                  <div className="line-note-label">What this does</div>
                  <MarkdownRenderer
                    text={noteText}
                    style={{ fontSize: 13, lineHeight: 1.65 }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
