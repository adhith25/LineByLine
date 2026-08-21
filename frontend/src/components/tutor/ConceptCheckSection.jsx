import React from 'react';
import ConceptCheck from '../ConceptCheck';
import { CheckCircle, HelpCircle } from 'lucide-react';

export default function ConceptCheckSection({
  checkData,
  onAnswerSubmitted,
  stageIndex = 3,
}) {
  if (!checkData) return null;

  const stageStyle = { '--stage-index': stageIndex };

  return (
    <div className="stage-group stage-fade check-stage" style={stageStyle}>
      <div className="stage-meta">
        <span
          className="stage-dot stage-dot-success"
          aria-hidden="true"
        />
        <div>
          <span className="stage-kicker">Step 4 · Check Understanding</span>
          <h3 className="stage-title">
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <CheckCircle size={16} style={{ color: 'var(--success)' }} />
              Concept Check
            </span>
          </h3>
        </div>
        <span className="pill-success" title="Answer to update mastery">
          <HelpCircle size={12} aria-hidden="true" />
          Quiz
        </span>
      </div>

      <ConceptCheck
        checkData={checkData}
        onAnswerSubmitted={onAnswerSubmitted}
      />
    </div>
  );
}
