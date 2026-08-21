import React, { useRef } from 'react';

export default function CodeEditor({
  code,
  setCode,
  language,
  setLanguage,
}) {
  const lineNumbersRef = useRef(null);
  const lineCount = Math.max(1, code.split('\n').length);
  const lineNumbersArray = Array.from({ length: lineCount }, (_, i) => i + 1);

  const handleScroll = (e) => {
    if (lineNumbersRef.current) {
      lineNumbersRef.current.scrollTop = e.target.scrollTop;
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        flex: 1,
        minHeight: 0,
        overflow: 'hidden',
      }}
    >
      <div className="editor-controls" style={{ flexShrink: 0 }}>
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

      <div
        className="editor-wrapper"
        style={{
          flex: 1,
          minHeight: 0,
          display: 'flex',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div
          ref={lineNumbersRef}
          className="line-numbers"
          style={{
            overflow: 'hidden',
            flexShrink: 0,
            userSelect: 'none',
          }}
        >
          {lineNumbersArray.map((num) => (
            <div key={num}>{num}</div>
          ))}
        </div>
        <textarea
          className="code-textarea"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          onScroll={handleScroll}
          placeholder="Paste or type your code here..."
          spellCheck="false"
          style={{
            flex: 1,
            height: '100%',
            minHeight: 0,
            overflow: 'auto',
          }}
        />
      </div>
    </div>
  );
}
