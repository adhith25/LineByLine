import React, { useState } from 'react';
import MarkdownRenderer from './MarkdownRenderer';

export default function ConceptCheck({ checkData, onAnswerSubmitted }) {
  if (!checkData || !checkData.options || checkData.options.length === 0) {
    return null;
  }

  const { question, options, correct_index, explanation } = checkData;
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    if (selectedIndex === null) return;
    setSubmitted(true);
    const correct = selectedIndex === correct_index;
    if (onAnswerSubmitted) {
      onAnswerSubmitted(correct);
    }
  };


  const handleReset = () => {
    setSelectedIndex(null);
    setSubmitted(false);
  };

  const isCorrect = selectedIndex === correct_index;

  return (
    <div
      className="card-box"
      style={{
        border: '1px solid rgba(59, 130, 246, 0.35)',
        background: 'rgba(59, 130, 246, 0.05)',
      }}
    >
      <div className="card-title" style={{ color: '#60a5fa' }}>
        <span>🎯</span>
        <span>Concept Check Quiz</span>
      </div>

      <p style={{ fontSize: 14.5, fontWeight: 600, color: '#f3f4f6', marginBottom: 16, lineHeight: 1.6 }}>
        <MarkdownRenderer
          text={question}
          style={{ fontSize: 14.5, fontWeight: 600, color: '#f3f4f6', lineHeight: 1.6 }}
        />
      </p>

      {/* Options List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
        {options.map((opt, idx) => {
          let optionStyle = {
            padding: '10px 14px',
            borderRadius: 8,
            border: '1px solid var(--border-color)',
            background: 'var(--bg-card)',
            color: 'var(--text-primary)',
            fontSize: 13,
            cursor: submitted ? 'default' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            transition: 'all 0.2s ease',
          };

          if (!submitted && selectedIndex === idx) {
            optionStyle.borderColor = '#3b82f6';
            optionStyle.background = 'rgba(59, 130, 246, 0.15)';
          }

          if (submitted) {
            if (idx === correct_index) {
              optionStyle.borderColor = '#10b981';
              optionStyle.background = 'rgba(16, 185, 129, 0.15)';
              optionStyle.color = '#34d399';
            } else if (idx === selectedIndex && !isCorrect) {
              optionStyle.borderColor = '#ef4444';
              optionStyle.background = 'rgba(239, 68, 68, 0.15)';
              optionStyle.color = '#fca5a5';
            }
          }

          return (
            <div
              key={idx}
              style={optionStyle}
              onClick={() => !submitted && setSelectedIndex(idx)}
            >
              <span
                style={{
                  width: 22,
                  height: 22,
                  borderRadius: '50%',
                  border: '1px solid currentColor',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 11,
                  fontWeight: 600,
                }}
              >
                {String.fromCharCode(65 + idx)}
              </span>
              <span>{opt}</span>
              {submitted && idx === correct_index && (
                <span style={{ marginLeft: 'auto', fontWeight: 700 }}>✓ Correct</span>
              )}
              {submitted && idx === selectedIndex && !isCorrect && (
                <span style={{ marginLeft: 'auto', fontWeight: 700 }}>✗ Your answer</span>
              )}
            </div>
          );
        })}
      </div>

      {/* Submit Button */}
      {!submitted ? (
        <button
          className="btn-primary"
          style={{ width: 'auto', fontSize: 13, padding: '8px 18px' }}
          onClick={handleSubmit}
          disabled={selectedIndex === null}
        >
          Check Answer
        </button>
      ) : (
        <div style={{ marginTop: 12 }}>
          <div
            style={{
              padding: '12px 14px',
              borderRadius: 8,
              background: isCorrect ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
              border: `1px solid ${isCorrect ? '#10b981' : '#ef4444'}`,
              marginBottom: 12,
            }}
          >
            <div style={{ fontWeight: 700, fontSize: 14.5, color: isCorrect ? '#34d399' : '#fca5a5', marginBottom: 6 }}>
              {isCorrect ? '🎉 Correct!' : '❌ Incorrect'}
            </div>
            <MarkdownRenderer
              text={explanation}
              style={{ fontSize: 13, color: '#e5e7eb', lineHeight: 1.6 }}
            />
          </div>

          <button
            className="btn-secondary"
            onClick={handleReset}
            style={{ fontSize: 12 }}
          >
            ↺ Try Quiz Again
          </button>
        </div>
      )}
    </div>
  );
}
