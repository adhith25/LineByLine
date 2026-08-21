import React, { useState } from 'react';
import ConceptTeaching from '../ConceptTeaching';
import { ChevronDown, ChevronUp, GraduationCap, Loader2 } from 'lucide-react';

export default function ConceptTeachingSection({
  teachingData,
  isLoading,
  stageIndex = 2,
}) {
  const [open, setOpen] = useState(true);
  const hasData = !!teachingData && Object.keys(teachingData).length > 0;
  const showSection = hasData || isLoading;

  if (!showSection) return null;

  const stageStyle = { '--stage-index': stageIndex };

  return (
    <div className="stage-group stage-fade teach-stage" style={stageStyle}>
      <div className="stage-meta">
        <span
          className="stage-dot stage-dot-accent"
          aria-hidden="true"
        />
        <div>
          <span className="stage-kicker">Step 3 · Concept Teaching</span>
          <h3 className="stage-title">
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <GraduationCap size={16} style={{ color: 'var(--accent-primary)' }} />
              {teachingData?.concept
                ? `Learn: ${teachingData.concept}`
                : isLoading
                  ? 'Preparing concept lesson…'
                  : 'Concept Lesson'}
            </span>
          </h3>
        </div>
        {isLoading && (
          <Loader2
            size={15}
            style={{
              color: 'var(--accent-primary)',
              animation: 'spin 0.8s linear infinite',
              marginLeft: 'auto',
            }}
            aria-hidden="true"
          />
        )}
      </div>

      {hasData ? (
        <section
          className="collapsible-card card-box concept-teach-card"
          aria-label="Concept teaching"
        >
          <button
            className="collapsible-trigger"
            onClick={() => setOpen((o) => !o)}
            aria-expanded={open}
            aria-controls="teaching-panel"
          >
            <span className="collapsible-title">
              <GraduationCap size={15} aria-hidden="true" />
              <span>Teaching Notes</span>
            </span>
            {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          {open && (
            <div id="teaching-panel" className="collapsible-panel">
              <ConceptTeaching
                teachingData={teachingData}
                isLoading={false}
              />
            </div>
          )}
        </section>
      ) : (
        <section className="card-box stage-skeleton-mini" aria-busy="true">
          <div className="skeleton skeleton-line medium" />
          <div className="skeleton skeleton-line" />
          <div className="skeleton skeleton-line short" />
          <div className="skeleton skeleton-box" />
        </section>
      )}
    </div>
  );
}
