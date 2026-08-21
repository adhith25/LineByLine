import React from 'react';
import Misconception from '../Misconception';
import { AlertTriangle } from 'lucide-react';

export default function MisconceptionInsight({
  analysisResult,
  onLearnConcept,
  isLoading,
  stageIndex = 1,
}) {
  const misconceptionData = analysisResult?.possible_misconception;
  const hasData =
    !!misconceptionData &&
    (!!misconceptionData.title ||
      !!misconceptionData.concept_name ||
      !!misconceptionData.description);

  if (!hasData) return null;

  const stageStyle = { '--stage-index': stageIndex };

  return (
    <div className="stage-group stage-fade misconception-stage" style={stageStyle}>
      <div className="stage-meta">
        <span
          className="stage-dot stage-dot-warning"
          aria-hidden="true"
        />
        <div>
          <span className="stage-kicker">
            Step 2 · Possible Misunderstanding
          </span>
          <h3 className="stage-title">
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <AlertTriangle size={16} style={{ color: 'var(--warning)' }} />
              Misconception Insight
            </span>
          </h3>
        </div>
      </div>

      <Misconception
        misconceptionData={misconceptionData}
        onLearnConcept={onLearnConcept}
        isLoading={isLoading}
      />
    </div>
  );
}
