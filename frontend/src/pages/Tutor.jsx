import React, { useState, useEffect } from 'react';
import CodeEditor from '../components/CodeEditor';
import PersonaSelector from '../components/PersonaSelector';
import AnalyzeButton from '../components/AnalyzeButton';
import LineExplanation from '../components/LineExplanation';
import Misconception from '../components/Misconception';
import ConceptTeaching from '../components/ConceptTeaching';
import ConceptCheck from '../components/ConceptCheck';
import Progress from '../components/Progress';
import Recommendation from '../components/Recommendation';
import MarkdownRenderer from '../components/MarkdownRenderer';
import {
  explainCode,
  teachConcept,
  fetchConceptCheck,
  sendFollowup,
  fetchProgress,
  submitQuizResult,
  fetchRecommendations,
} from '../services/api';

const DEFAULT_CODE = '';

const QUICK_ACTIONS = [
  { id: 'simpler', label: '🐣 Explain simpler' },
  { id: 'eli5', label: "👶 Explain like I'm 5" },
  { id: 'analogy', label: '🌍 Real-world analogy' },
  { id: 'example', label: '📌 Show example' },
  { id: 'visualize', label: '🔍 Visualize step-by-step' },
  { id: 'deeper', label: '🚀 Go deeper' },
  { id: 'mistakes', label: '⚠️ Common mistakes' },
];

export default function Tutor() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [language, setLanguage] = useState('python');
  const [persona, setPersona] = useState('academic');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const [analysisResult, setAnalysisResult] = useState(null);

  // Teaching & Quiz State
  const [isTeachingLoading, setIsTeachingLoading] = useState(false);
  const [teachingData, setTeachingData] = useState(null);
  const [conceptCheckData, setConceptCheckData] = useState(null);

  // Progress State
  const [progressData, setProgressData] = useState(null);
  const [isProgressLoading, setIsProgressLoading] = useState(false);
  const [recommendationData, setRecommendationData] = useState(null);
  const [isRecommendationLoading, setIsRecommendationLoading] = useState(false);
  
  // Follow-up state
  const [chatHistory, setChatHistory] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isFollowupLoading, setIsFollowupLoading] = useState(false);

  const refreshProgress = async () => {
    setIsProgressLoading(true);
    try {
      const data = await fetchProgress();
      setProgressData(data);
    } catch (err) {
      console.error('Failed to fetch progress:', err);
    } finally {
      setIsProgressLoading(false);
    }
  };

  const refreshRecommendations = async () => {
    setIsRecommendationLoading(true);
    try {
      const data = await fetchRecommendations();
      setRecommendationData(data);
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
    } finally {
      setIsRecommendationLoading(false);
    }
  };

  useEffect(() => {
    refreshProgress();
    refreshRecommendations();
  }, []);

  const handleAnalyze = async () => {
    if (!code.trim()) {
      setError('Please enter some code before requesting an explanation.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setChatHistory([]);
    setTeachingData(null);
    setConceptCheckData(null);

    try {
      const result = await explainCode({
        code,
        mode: persona,
        language,
      });

      setAnalysisResult(result);
      
      // Populate concept teaching / check if provided
      if (result.concept_teaching) {
        setTeachingData(result.concept_teaching);
      }
      if (result.concept_check) {
        setConceptCheckData(result.concept_check);
      }

      // Refresh progress metrics after submission
      await refreshProgress();
      await refreshRecommendations();
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(err.message || 'Failed to generate explanation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLearnConcept = async () => {
    if (!analysisResult) return;
    const misc = analysisResult.possible_misconception || {};
    const conceptName = misc.concept_name || misc.title || 'Core Programming Mechanics';
    const description = misc.description || '';

    setIsTeachingLoading(true);
    try {
      const teachRes = await teachConcept({
        code,
        misconception: description,
        concept: conceptName,
        mode: persona,
        language,
      });
      setTeachingData(teachRes);

      const quizRes = await fetchConceptCheck({
        code,
        concept: conceptName,
        mode: persona,
        language,
      });
      setConceptCheckData(quizRes);
    } catch (err) {
      console.error('Learning concept failed:', err);
      setError('Failed to fetch concept lesson: ' + err.message);
    } finally {
      setIsTeachingLoading(false);
    }
  };

  const handleQuizAnswer = async (isCorrect) => {
    const conceptName =
      (teachingData && teachingData.concept) ||
      (analysisResult && analysisResult.possible_misconception
        ? analysisResult.possible_misconception.concept_name || analysisResult.possible_misconception.title
        : 'Zero-Based Indexing');

    try {
      await submitQuizResult({
        concept: conceptName,
        isCorrect,
      });
      await refreshProgress();
      await refreshRecommendations();
    } catch (err) {
      console.error('Submitting quiz result failed:', err);
    }
  };

  const handleClear = () => {
    setCode('');
    setAnalysisResult(null);
    setTeachingData(null);
    setConceptCheckData(null);
    setError(null);
    setChatHistory([]);
  };

  const handleSendFollowup = async (action = null, textOverride = null) => {
    const userMsg = textOverride || chatInput;
    if (!userMsg && !action) return;

    const currentExp = analysisResult ? analysisResult.explanation : '';
    
    const userTurn = { role: 'user', content: action ? `[Action: ${action}]` : userMsg };
    setChatHistory((prev) => [...prev, userTurn]);
    if (!action) setChatInput('');

    setIsFollowupLoading(true);

    try {
      const res = await sendFollowup({
        message: userMsg,
        action,
        code,
        language,
        current_explanation: currentExp,
      });

      const assistantTurn = { role: 'assistant', content: res.reply };
      setChatHistory((prev) => [...prev, assistantTurn]);
    } catch (err) {
      console.error('Followup failed:', err);
      setError('Follow-up query failed: ' + err.message);
    } finally {
      setIsFollowupLoading(false);
    }
  };

  return (
    <div className="tutor-container">
      {/* LEFT PANEL: Code Input & Persona Setup */}
      <section className="tutor-panel">
        <div className="panel-header">
          <span className="panel-title">
            <span>💻</span> Code Input & Persona
          </span>
        </div>

        <div style={{ padding: '12px 20px 0' }}>
          <span className="control-label" style={{ display: 'block', marginBottom: 8 }}>
            Select Tutor Persona
          </span>
          <PersonaSelector
            selectedPersona={persona}
            onSelectPersona={setPersona}
          />
        </div>

        <CodeEditor
          code={code}
          setCode={setCode}
          language={language}
          setLanguage={setLanguage}
          onClear={handleClear}
        />

        <div className="editor-footer">
          <AnalyzeButton
            onAnalyze={handleAnalyze}
            isLoading={isLoading}
            persona={persona}
          />
        </div>
      </section>

      {/* RIGHT PANEL: AI Tutor Output & Progress */}
      <section className="tutor-panel">
        <div className="panel-header">
          <span className="panel-title">
            <span>🤖</span> AI Tutor Analysis
          </span>
          {analysisResult && (
            <span
              style={{
                fontSize: 12,
                background: 'rgba(99, 102, 241, 0.15)',
                color: 'var(--accent-primary)',
                padding: '2px 8px',
                borderRadius: 12,
                fontWeight: 600,
                textTransform: 'capitalize',
              }}
            >
              Mode: {analysisResult.mode_used || persona}
            </span>
          )}
        </div>

        <div className="output-body">
          {error && (
            <div className="error-banner">
              <span>⚠️</span>
              <div>{error}</div>
            </div>
          )}

          {/* Persistent Learning Progress Overview */}
          <Progress progressData={progressData} isLoading={isProgressLoading} />

          {isLoading && (
            <>
              <div className="loading-state">
                <div className="spinner" />
                <p>Analyzing code structure & preparing line-by-line breakdown...</p>
              </div>
              <LineExplanation lineExplanations={null} isLoading={true} />
            </>
          )}

          {!isLoading && !analysisResult && !error && (
            <div className="empty-state">
              <span className="empty-icon">🔭</span>
              <h3 style={{ fontSize: 16, color: 'var(--text-primary)' }}>No Explanation Yet</h3>
              <p style={{ fontSize: 13 }}>
                Paste or write your code on the left, choose your preferred tutor persona, and click <strong>Analyze & Explain Code</strong>.
              </p>
            </div>
          )}

          {!isLoading && analysisResult && (
            <>
              {/* High-level explanation card */}
              <div className="card-box card-overview">
                <div className="card-title">
                  <span>📖</span>
                  <span>Code Overview</span>
                </div>
                <MarkdownRenderer text={analysisResult.explanation} />
              </div>

              {/* Line-by-line breakdown component */}
              <LineExplanation
                lineExplanations={analysisResult.line_explanations}
              />

              {/* Integrated Possible Misconception Section */}
              <Misconception
                misconceptionData={analysisResult.possible_misconception}
                onLearnConcept={handleLearnConcept}
                isLoading={isTeachingLoading}
              />

              {/* Concept Teaching Panel */}
              <ConceptTeaching
                teachingData={teachingData}
                isLoading={isTeachingLoading}
              />

              {/* Concept Check Quiz Component */}
              <ConceptCheck
                checkData={conceptCheckData}
                onAnswerSubmitted={handleQuizAnswer}
              />

              {/* Phase 5: Verified Learning Recommendations */}
              <Recommendation
                recommendationData={recommendationData}
                isLoading={isRecommendationLoading}
              />

              {/* Follow-up Chat Panel */}
              <div className="card-box">
                <div className="card-title">
                  <span>💬</span>
                  <span>Follow-Up & Questions</span>
                </div>

                <div className="quick-actions" style={{ marginBottom: 12 }}>
                  {QUICK_ACTIONS.map((act) => (
                    <button
                      key={act.id}
                      className="qa-chip"
                      onClick={() => handleSendFollowup(act.id)}
                      disabled={isFollowupLoading}
                    >
                      {act.label}
                    </button>
                  ))}
                </div>

                <div className="chat-log" style={{ marginBottom: 12 }}>
                  {chatHistory.length === 0 && !isFollowupLoading && (
                    <div className="chat-empty">
                      💡 No questions yet — try a Quick Action above or ask anything about the explanation!
                    </div>
                  )}
                  {chatHistory.map((turn, i) => (
                    <div key={i} className={`chat-bubble ${turn.role}`}>
                      {turn.role === 'assistant' ? (
                        <MarkdownRenderer
                          text={turn.content}
                          style={{ fontSize: 13, color: 'inherit', lineHeight: 1.55 }}
                        />
                      ) : (
                        turn.content
                      )}
                    </div>
                  ))}
                  {isFollowupLoading && (
                    <div className="chat-bubble assistant">
                      <div className="typing-indicator">
                        <span />
                        <span />
                        <span />
                        <span style={{ marginLeft: 8, fontSize: 12, color: 'var(--text-secondary)' }}>
                          Tutor is thinking...
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                <div className="chat-input-container">
                  <input
                    type="text"
                    className="chat-input"
                    placeholder="Ask a follow-up question..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleSendFollowup();
                    }}
                  />
                  <button
                    className="btn-send"
                    onClick={() => handleSendFollowup()}
                    disabled={isFollowupLoading || !chatInput.trim()}
                  >
                    Send
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
}
