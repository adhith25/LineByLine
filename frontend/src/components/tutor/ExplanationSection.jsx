import React, { useState } from 'react';
import LineExplanation from '../LineExplanation';
import MarkdownRenderer from '../MarkdownRenderer';
import { ChevronDown, ChevronUp, BookOpen, Code2 } from 'lucide-react';

export default function ExplanationSection({ analysisResult, stageIndex = 0 }) {
  const [overviewOpen, setOverviewOpen] = useState(true);
  const [lineOpen, setLineOpen] = useState(true);

  if (!analysisResult) return null;
  const stageStyle = { '--stage-index': stageIndex };

  return (
    <div className="stage-group stage-fade" style={stageStyle}>
      <div className="stage-meta">
        <span className="stage-dot" aria-hidden="true" />
        <div>
          <span className="stage-kicker">Step 1 · Analysis</span>
          <h3 className="stage-title">Code Explanation</h3>
        </div>
      </div>

      <section
        className="collapsible-card card-box"
        aria-label="Code overview explanation"
      >
        <button
          className="collapsible-trigger"
          onClick={() => setOverviewOpen((o) => !o)}
          aria-expanded={overviewOpen}
          aria-controls="explanation-overview-panel"
        >
          <span className="collapsible-title">
            <BookOpen size={15} aria-hidden="true" />
            <span>Code Overview</span>
          </span>
          {overviewOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
        {overviewOpen && (
          <div id="explanation-overview-panel" className="collapsible-panel">
            <MarkdownRenderer text={analysisResult.explanation} />
          </div>
        )}
      </section>

      {analysisResult.line_explanations &&
        analysisResult.line_explanations.length > 0 && (
          <section
            className="collapsible-card card-box line-breakdown-card"
            aria-label="Line by line breakdown"
          >
            <button
              className="collapsible-trigger"
              onClick={() => setLineOpen((o) => !o)}
              aria-expanded={lineOpen}
              aria-controls="explanation-lines-panel"
            >
              <span className="collapsible-title">
                <Code2 size={15} aria-hidden="true" />
                <span>Line-by-Line Breakdown</span>
                <span className="pill-secondary">
                  {analysisResult.line_explanations.length} lines
                </span>
              </span>
              {lineOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>
            {lineOpen && (
              <div id="explanation-lines-panel" className="collapsible-panel">
                <LineExplanation
                  lineExplanations={analysisResult.line_explanations}
                />
              </div>
            )}
          </section>
        )}
    </div>
  );
}
