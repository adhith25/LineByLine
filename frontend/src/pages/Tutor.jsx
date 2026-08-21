import React, { useState, useEffect, useMemo } from 'react';
import CodeEditor from '../components/CodeEditor';
import PersonaSelector from '../components/PersonaSelector';
import AnalyzeButton from '../components/AnalyzeButton';
import MarkdownRenderer from '../components/MarkdownRenderer';
import ExplanationSection from '../components/tutor/ExplanationSection';
import MisconceptionInsight from '../components/tutor/MisconceptionInsight';
import ConceptTeachingSection from '../components/tutor/ConceptTeachingSection';
import ConceptCheckSection from '../components/tutor/ConceptCheckSection';
import NextStepTeaser from '../components/tutor/NextStepTeaser';
import {
  explainCode,
  teachConcept,
  fetchConceptCheck,
  sendFollowup,
  fetchProgress,
  submitQuizResult,
  fetchRecommendations,
} from '../services/api';
import { MessageSquarePlus, Bot, ChevronDown, ChevronUp } from 'lucide-react';

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

const LOADING_MESSAGES = [
  'Analyzing your code structure…',
  'Understanding the logic and intent…',
  'Identifying important concepts…',
  'Preparing your personalized learning guidance…',
];

export default function Tutor() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [language, setLanguage] = useState('python');
  const [persona, setPersona] = useState('academic');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [loadingMessageIdx, setLoadingMessageIdx] = useState(0);

  const [analysisResult, setAnalysisResult] = useState(null);

  const [isTeachingLoading, setIsTeachingLoading] = useState(false);
  const [teachingData, setTeachingData] = useState(null);
  const [conceptCheckData, setConceptCheckData] = useState(null);

  const [progressData, setProgressData] = useState(null);
  const [isProgressLoading, setIsProgressLoading] = useState(false);
  const [recommendationData, setRecommendationData] = useState(null);
  const [isRecommendationLoading, setIsRecommendationLoading] = useState(false);

  const [chatHistory, setChatHistory] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isFollowupLoading, setIsFollowupLoading] = useState(false);
  const [chatOpen, setChatOpen] = useState(true);

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
    if (!isLoading) return undefined;
    setLoadingMessageIdx(0);
    const id = setInterval(() => {
      setLoadingMessageIdx((prev) =>
        prev < LOADING_MESSAGES.length - 1 ? prev + 1 : prev
      );
    }, 1400);
    return () => clearInterval(id);
  }, [isLoading]);

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
    setChatOpen(true);

    try {
      const result = await explainCode({
        code,
        mode: persona,
        language,
      });

      setAnalysisResult(result);

      if (result.concept_teaching) {
        setTeachingData(result.concept_teaching);
      }
      if (result.concept_check) {
        setConceptCheckData(result.concept_check);
      }

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
    const conceptName =
      misc.concept_name || misc.title || 'Core Programming Mechanics';
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
        ? analysisResult.possible_misconception.concept_name ||
          analysisResult.possible_misconception.title
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

    const userTurn = {
      role: 'user',
      content: action ? `[Action: ${action}]` : userMsg,
    };
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

  const showFollowup = useMemo(
    () => !!analysisResult,
    [analysisResult]
  );

  return (
    <div className="tutor-container">
      {/* LEFT PANEL: Code Input & Persona Setup */}
      <section className="tutor-panel">
        <div className="panel-header" style={{ flexShrink: 0 }}>
          <span className="panel-title">
            <span>💻</span> Code Workspace
          </span>
        </div>

        <div style={{ padding: '12px 20px 0', flexShrink: 0 }}>
          <span
            className="control-label"
            style={{ display: 'block', marginBottom: 8 }}
          >
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
        />

        <div className="editor-footer" style={{ flexShrink: 0, display: 'flex', gap: 12, alignItems: 'center' }}>
          <button
            className="btn-secondary"
            onClick={handleClear}
            style={{ width: 'auto', flexShrink: 0, padding: '10px 14px', fontSize: 13 }}
            title="Clear the code editor"
          >
            ✕ Clear Editor
          </button>
          <div style={{ flex: 1, minWidth: 0 }}>
            <AnalyzeButton
              onAnalyze={handleAnalyze}
              isLoading={isLoading}
              persona={persona}
            />
          </div>
        </div>
      </section>

      {/* RIGHT PANEL: AI Learning Flow — staged progressive disclosure */}
      <section className="tutor-panel">
        <div className="panel-header">
          <span className="panel-title">
            <Bot size={15} aria-hidden="true" style={{ color: 'var(--accent-primary)' }} />
            AI Tutor
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

        <div className="output-body output-body--tutor">
          {error && (
            <div className="error-banner" role="alert">
              <span>⚠️</span>
              <div>{error}</div>
            </div>
          )}

          {isLoading && (
            <div className="loading-tutor card-box">
              <div className="loading-tutor-header">
                <div className="spinner" aria-hidden="true" />
                <div>
                  <span className="loading-tutor-title">
                    {LOADING_MESSAGES[loadingMessageIdx]}
                  </span>
                  <span className="loading-tutor-sub">
                    Building your personalized learning journey…
                  </span>
                </div>
              </div>
              <div className="loading-steps" aria-hidden="true">
                {['Code', 'Explanation', 'Misconception', 'Concept', 'Check', 'Next'].map(
                  (s, i) => (
                    <div
                      key={s}
                      className={`loading-step${
                        loadingMessageIdx + 1 >= i ? ' active' : ''
                      }`}
                    >
                      <span className="loading-step-dot" />
                      <span>{s}</span>
                    </div>
                  )
                )}
              </div>
            </div>
          )}

          {!isLoading && !analysisResult && !error && (
            <div className="empty-state tutor-empty">
              <span className="empty-icon">🔭</span>
              <h3 style={{ fontSize: 16, color: 'var(--text-primary)' }}>
                No Explanation Yet
              </h3>
              <p style={{ fontSize: 13 }}>
                Paste or write your code on the left, choose your preferred
                tutor persona, and click{' '}
                <strong>Analyze &amp; Explain Code</strong> to begin your
                learning journey.
              </p>
              <ol className="tutor-empty-flow">
                <li>
                  <span>1</span>Write or paste code
                </li>
                <li>
                  <span>2</span>Select a tutor persona
                </li>
                <li>
                  <span>3</span>Analyze to unlock the 6-step learning path
                </li>
              </ol>
            </div>
          )}

          {!isLoading && analysisResult && (
            <>
              <ExplanationSection
                analysisResult={analysisResult}
                stageIndex={0}
              />

              <MisconceptionInsight
                analysisResult={analysisResult}
                onLearnConcept={handleLearnConcept}
                isLoading={isTeachingLoading}
                stageIndex={1}
              />

              <ConceptTeachingSection
                teachingData={teachingData}
                isLoading={isTeachingLoading}
                stageIndex={2}
              />

              <ConceptCheckSection
                checkData={conceptCheckData}
                onAnswerSubmitted={handleQuizAnswer}
                stageIndex={3}
              />

              <NextStepTeaser
                recommendationData={recommendationData}
                isLoading={isRecommendationLoading}
                stageIndex={4}
              />

              {showFollowup && (
                <div className="stage-group stage-fade chat-stage" style={{ '--stage-index': 5 }}>
                  <div className="stage-meta">
                    <span className="stage-dot" aria-hidden="true" />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <span className="stage-kicker">Step 6 · Ask Anything</span>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <h3 className="stage-title">
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                            <MessageSquarePlus size={16} style={{ color: 'var(--accent-primary)' }} />
                            Follow-Up &amp; Questions
                          </span>
                        </h3>
                        <button
                          className="chat-collapse"
                          onClick={() => setChatOpen((o) => !o)}
                          aria-expanded={chatOpen}
                          aria-controls="followup-panel"
                          aria-label={chatOpen ? 'Collapse chat' : 'Expand chat'}
                        >
                          {chatOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                        </button>
                      </div>
                    </div>
                  </div>

                  {chatOpen && (
                    <div id="followup-panel" className="card-box followup-panel">
                      <div
                        className="quick-actions"
                        style={{ marginBottom: 12, flexWrap: 'wrap' }}
                      >
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
                            💡 No questions yet — try a Quick Action above or
                            ask anything about the explanation!
                          </div>
                        )}
                        {chatHistory.map((turn, i) => (
                          <div key={i} className={`chat-bubble ${turn.role}`}>
                            {turn.role === 'assistant' ? (
                              <MarkdownRenderer
                                text={turn.content}
                                style={{
                                  fontSize: 13,
                                  color: 'inherit',
                                  lineHeight: 1.55,
                                }}
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
                              <span
                                style={{
                                  marginLeft: 8,
                                  fontSize: 12,
                                  color: 'var(--text-secondary)',
                                }}
                              >
                                Tutor is thinking…
                              </span>
                            </div>
                          </div>
                        )}
                      </div>

                      <div className="chat-input-container">
                        <input
                          type="text"
                          className="chat-input"
                          placeholder="Ask a follow-up question…"
                          value={chatInput}
                          onChange={(e) => setChatInput(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleSendFollowup();
                          }}
                          aria-label="Follow-up question"
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
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </section>
    </div>
  );
}
