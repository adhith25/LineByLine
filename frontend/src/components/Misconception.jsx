import React from 'react';
import MarkdownRenderer from './MarkdownRenderer';

/**
 * Integrated "Possible Misconception" Section
 * Rendered inside the AI Tutor Analysis panel.
 * Uses cautious phrasing ("Possible Misconception", "You may be...").
 */
export default function Misconception({ misconceptionData, onLearnConcept, isLoading }) {
  if (!misconceptionData) return null;

  const title = misconceptionData.title || misconceptionData.concept_name || 'Code Logic & Mechanics';
  const rawDescription = misconceptionData.description || 'You may be confusing core concepts in this code block.';
  
  // Ensure cautious phrasing
  const cautiousDescription = rawDescription.startsWith('You have')
    ? rawDescription.replace(/^You have/i, 'You may be experiencing')
    : rawDescription;

  return (
    <div
      className="card-box"
      style={{
        border: '1px solid rgba(245, 158, 11, 0.35)',
        background: 'rgba(245, 158, 11, 0.05)',
      }}
    >
      <div className="card-title" style={{ color: '#fbbf24' }}>
        <span>⚠️</span>
        <span>Possible Misconception</span>
      </div>

      <div style={{ marginBottom: 12 }}>
        <h4 style={{ fontSize: 15, color: '#fef08a', marginBottom: 8, fontWeight: 700 }}>
          {title}
        </h4>
        <div style={{ fontSize: 13, color: '#fde68a' }}>
          <MarkdownRenderer
            text={`"${cautiousDescription}"`}
            style={{ fontSize: 13, color: '#fde68a', lineHeight: 1.65 }}
          />
        </div>
      </div>

      <button
        className="btn-primary"
        style={{
          background: 'linear-gradient(135deg, #d97706 0%, #b45309 100%)',
          boxShadow: '0 0 16px rgba(217, 119, 6, 0.3)',
          fontSize: 13,
          padding: '8px 16px',
          width: 'auto',
          marginTop: 8,
        }}
        onClick={onLearnConcept}
        disabled={isLoading}
      >
        {isLoading ? 'Loading Concept Lesson...' : 'Learn This Concept →'}
      </button>
    </div>
  );
}
