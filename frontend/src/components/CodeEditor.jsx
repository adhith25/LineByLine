import React from 'react';

export default function CodeEditor({
  code,
  setCode,
  language,
  setLanguage,
  onClear,
}) {
  const lineCount = Math.max(1, code.split('\n').length);
  const lineNumbersArray = Array.from({ length: lineCount }, (_, i) => i + 1);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
      <div className="editor-controls">
        <div className="control-row">
          <span className="control-label">Language</span>
          <select
            className="select-input"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
            <option value="typescript">TypeScript</option>
          </select>
        </div>
      </div>

      <div className="editor-wrapper">
        <div className="line-numbers">
          {lineNumbersArray.map((num) => (
            <div key={num}>{num}</div>
          ))}
        </div>
        <textarea
          className="code-textarea"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Paste or type your code here..."
          spellCheck="false"
        />
      </div>

      <div className="editor-footer">
        <button className="btn-secondary" onClick={onClear}>
          ✕ Clear Editor
        </button>
      </div>
    </div>
  );
}
