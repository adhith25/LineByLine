import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles, Target, BookOpen } from 'lucide-react';

export default function NextStepTeaser({
  recommendationData,
  isLoading,
  stageIndex = 4,
}) {
  const hasData =
    !!recommendationData &&
    (!!recommendationData.recommended_action ||
      !!recommendationData.primary_concept ||
      !!recommendationData.rationale ||
      (recommendationData.next_steps && recommendationData.next_steps.length > 0));

  if (!hasData && !isLoading) return null;

  const stageStyle = { '--stage-index': stageIndex };

  return (
    <div className="stage-group stage-fade nextstage" style={stageStyle}>
      <div className="stage-meta">
        <span className="stage-dot stage-dot-accent" aria-hidden="true" />
        <div>
          <span className="stage-kicker">Step 5 · Next Step</span>
          <h3 className="stage-title">
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <Sparkles size={16} style={{ color: 'var(--accent-primary)' }} />
              Personalized Next Step
            </span>
          </h3>
        </div>
      </div>

      {isLoading && !hasData ? (
        <section className="card-box stage-skeleton-mini next-skeleton">
          <div className="skeleton skeleton-line short" style={{ marginBottom: 10 }} />
          <div className="skeleton skeleton-line medium" />
          <div className="skeleton skeleton-line" />
        </section>
      ) : (
        <section
          className="card-box next-step-card"
          aria-label="Recommended next step"
        >
          {recommendationData.primary_concept && (
            <div className="next-step-hero">
              <div className="next-step-concept-wrap">
                <span className="next-step-label">
                  <Target size={13} aria-hidden="true" />
                  Recommended concept
                </span>
                <h4 className="next-step-concept">
                  {recommendationData.primary_concept}
                </h4>
              </div>
              <Link to="/progress" className="next-step-cta">
                <BookOpen size={15} aria-hidden="true" />
                <span>View full plan</span>
                <ArrowRight size={15} aria-hidden="true" />
              </Link>
            </div>
          )}

          {recommendationData.rationale && (
            <p className="next-step-rationale">
              {recommendationData.rationale}
            </p>
          )}

          {recommendationData.recommended_action && (
            <p className="next-step-action">
              {recommendationData.recommended_action}
            </p>
          )}

          {recommendationData.next_steps &&
            recommendationData.next_steps.length > 0 && (
              <ul className="next-step-list">
                {recommendationData.next_steps
                  .slice(0, 2)
                  .map((step, i) => (
                    <li key={i} className="next-step-item">
                      <span className="next-step-prio next-step-prio--low">
                        {step.priority || 'P' + (i + 1)}
                      </span>
                      <div className="next-step-item-body">
                        {step.action}
                        {step.estimated_minutes && (
                          <span className="next-step-meta">
                            · ~{step.estimated_minutes} min
                          </span>
                        )}
                      </div>
                    </li>
                  ))}
              </ul>
            )}

          <div className="next-step-footer">
            <span className="next-step-hint">
              See learning path, prerequisite graph and all resources on the
              Progress page.
            </span>
            <Link
              to="/progress"
              className="next-step-cta-link"
              aria-label="Go to Progress to see full learning plan"
            >
              Open Progress <ArrowRight size={14} aria-hidden="true" />
            </Link>
          </div>
        </section>
      )}
    </div>
  );
}
