import React from 'react';

/**
 * Lightweight zero-dependency Markdown renderer for AI tutor output.
 * Supports: ## / ### / #### headings, paragraphs (split by blank lines),
 * **bold**, `inline code`, - / * unordered lists, numbered lists,
 * literal \n escapes, and preformatted ```code blocks```.
 */
function renderInline(text) {
  const nodes = [];
  let buffer = '';
  let i = 0;

  const pushBuffer = () => {
    if (buffer) {
      nodes.push(buffer);
      buffer = '';
    }
  };

  while (i < text.length) {
    const ch = text[i];
    const next = text[i + 1];

    // Inline code: `code`
    if (ch === '`') {
      const end = text.indexOf('`', i + 1);
      if (end !== -1) {
        pushBuffer();
        nodes.push(
          <code key={`c-${i}`} style={styles.inlineCode}>
            {text.slice(i + 1, end)}
          </code>
        );
        i = end + 1;
        continue;
      }
    }

    // Bold: **text**
    if (ch === '*' && next === '*') {
      const end = text.indexOf('**', i + 2);
      if (end !== -1) {
        pushBuffer();
        nodes.push(
          <strong key={`b-${i}`} style={styles.bold}>
            {text.slice(i + 2, end)}
          </strong>
        );
        i = end + 2;
        continue;
      }
    }

    buffer += ch;
    i++;
  }
  pushBuffer();
  return nodes;
}

function cleanJsonArtifacts(raw) {
  if (!raw) return raw;
  let s = String(raw);

  // Always unescape literal \\n and \\" regardless of guard conditions
  s = s.replace(/\\n/g, '\n');
  s = s.replace(/\\"/g, '"');
  s = s.replace(/\\t/g, '\t');

  // If entire text IS a raw JSON string that leaked through, extract fields
  if (/^\s*\{[\s\S]*\}\s*$/.test(s.trim())) {
    // Try a real JSON parse first
    try {
      const parsed = JSON.parse(s.trim());
      if (parsed && typeof parsed === 'object' && parsed.explanation && typeof parsed.explanation === 'string') {
        return parsed.explanation;
      }
    } catch (_) {
      /* ignore — fall through to regex extraction */
    }
    // Regex fallback: pull "explanation" field content out of the raw JSON string
    const explMatch = /"explanation"\s*:\s*"((?:[^"\\]|\\.)*)"/.exec(s);
    if (explMatch && explMatch[1] && explMatch[1].length > 20) {
      s = explMatch[1]
        .replace(/\\n/g, '\n')
        .replace(/\\"/g, '"')
        .replace(/\\t/g, '\t')
        .replace(/\\\\/g, '\\');
    }
  }

  // Trim any stray closing-json tail artifacts (e.g., "  ]}" at end of text)
  s = s.replace(/\s*"\s*,\s*"(?:line_explanations|concept_teaching|concept_check|possible_misconception|complexity|mode_used)[\s\S]*$/gm, '');
  s = s.replace(/\s*\}\s*\]\s*\}\s*$/g, '');

  return s;
}

export default function MarkdownRenderer({ text, style }) {
  if (!text) return null;

  let cleaned = cleanJsonArtifacts(text);

  const rawBlocks = cleaned.split(/\n\s*\n/);
  const blocks = [];
  rawBlocks.forEach((b) => {
    const trimmed = b.trim();
    if (!trimmed) return;
    trimmed.split('\n').forEach((line) => blocks.push(line));
  });

  const elements = [];
  let listBuffer = null;
  let orderedListBuffer = null;

  const flushLists = () => {
    if (listBuffer) {
      elements.push(
        <ul key={`ul-${elements.length}`} style={styles.ul}>
          {listBuffer.map((item, idx) => (
            <li key={idx} style={styles.li}>{renderInline(item)}</li>
          ))}
        </ul>
      );
      listBuffer = null;
    }
    if (orderedListBuffer) {
      elements.push(
        <ol key={`ol-${elements.length}`} style={styles.ol}>
          {orderedListBuffer.map((item, idx) => (
            <li key={idx} style={styles.li}>{renderInline(item)}</li>
          ))}
        </ol>
      );
      orderedListBuffer = null;
    }
  };

  blocks.forEach((rawLine, idx) => {
    const line = rawLine.trim();
    if (!line) {
      flushLists();
      return;
    }

    // Code block (single ```line``` or fenced start)
    if (line.startsWith('```')) {
      flushLists();
      const codeContent = line.replace(/^```\w*\s?/, '').replace(/```$/, '').trim();
      if (codeContent) {
        elements.push(
          <pre key={`pre-${idx}`} style={styles.codeBlock}>
            <code>{codeContent}</code>
          </pre>
        );
      }
      return;
    }

    // Headings
    const h4 = /^####\s+(.+)$/.exec(line);
    const h3 = /^###\s+(.+)$/.exec(line);
    const h2 = /^##\s+(.+)$/.exec(line);
    const h1 = /^#\s+(.+)$/.exec(line);
    if (h4 || h3 || h2 || h1) {
      flushLists();
      const match = h4 || h3 || h2 || h1;
      const level = h4 ? 4 : h3 ? 3 : h2 ? 2 : 1;
      const style = level === 1 ? styles.h1 : level === 2 ? styles.h2 : level === 3 ? styles.h3 : styles.h4;
      const Tag = `h${level}`;
      elements.push(
        React.createElement(Tag, { key: `h-${idx}`, style }, renderInline(match[1]))
      );
      return;
    }

    // Unordered list: - or *
    const ul = /^[-*]\s+(.+)$/.exec(line);
    if (ul) {
      if (!listBuffer) listBuffer = [];
      listBuffer.push(ul[1]);
      return;
    }

    // Ordered list: 1. 2. etc
    const ol = /^\d+\.\s+(.+)$/.exec(line);
    if (ol) {
      if (!orderedListBuffer) orderedListBuffer = [];
      orderedListBuffer.push(ol[1]);
      return;
    }

    // Line label pattern: "Line 5:" or "Line 5 `code`:"
    const lineLabel = /^(Line\s*\d+)([:：]?)\s*(.*)$/i.exec(line);
    if (lineLabel && !ul && !ol) {
      flushLists();
      const [, num, sep, rest] = lineLabel;
      elements.push(
        <div key={`line-${idx}`} style={styles.lineLabelRow}>
          <span style={styles.lineLabel}>{num}{sep}</span>
          <span style={styles.lineLabelRest}>{renderInline(rest)}</span>
        </div>
      );
      return;
    }

    // Default paragraph (preserve inline \n -> space only if in same block)
    flushLists();
    elements.push(
      <p key={`p-${idx}`} style={styles.p}>
        {renderInline(line)}
      </p>
    );
  });

  flushLists();

  return <div style={{ ...styles.container, ...style }}>{elements}</div>;
}

const styles = {
  container: {
    color: '#e5e7eb',
    lineHeight: 1.75,
    fontSize: 14,
  },
  h1: {
    fontSize: 18,
    fontWeight: 700,
    color: '#f9fafb',
    marginTop: 4,
    marginBottom: 10,
    paddingBottom: 6,
    borderBottom: '1px solid rgba(255,255,255,0.08)',
    letterSpacing: 0.2,
  },
  h2: {
    fontSize: 16,
    fontWeight: 700,
    color: '#f3f4f6',
    marginTop: 16,
    marginBottom: 8,
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  h3: {
    fontSize: 14.5,
    fontWeight: 600,
    color: '#e5e7eb',
    marginTop: 12,
    marginBottom: 6,
  },
  h4: {
    fontSize: 13.5,
    fontWeight: 600,
    color: '#d1d5db',
    marginTop: 10,
    marginBottom: 4,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  p: {
    fontSize: 13.5,
    color: '#d1d5db',
    marginBottom: 8,
  },
  ul: {
    margin: '6px 0 10px 0',
    paddingLeft: 20,
    color: '#d1d5db',
  },
  ol: {
    margin: '6px 0 10px 0',
    paddingLeft: 22,
    color: '#d1d5db',
  },
  li: {
    fontSize: 13.5,
    marginBottom: 4,
    lineHeight: 1.6,
  },
  bold: {
    color: '#f3f4f6',
    fontWeight: 700,
  },
  inlineCode: {
    background: 'rgba(99,102,241,0.14)',
    color: '#c7d2fe',
    border: '1px solid rgba(99,102,241,0.28)',
    padding: '1px 6px',
    borderRadius: 4,
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: 12.5,
    margin: '0 2px',
  },
  codeBlock: {
    background: '#0a0d14',
    border: '1px solid rgba(255,255,255,0.08)',
    padding: '12px 14px',
    borderRadius: 8,
    color: '#c7d2fe',
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: 12.5,
    overflowX: 'auto',
    margin: '8px 0',
    lineHeight: 1.6,
  },
  lineLabelRow: {
    display: 'flex',
    gap: 10,
    alignItems: 'flex-start',
    padding: '8px 0',
  },
  lineLabel: {
    flexShrink: 0,
    background: 'rgba(99,102,241,0.15)',
    color: '#a5b4fc',
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: 11,
    fontWeight: 700,
    padding: '2px 8px',
    borderRadius: 4,
    marginTop: 2,
  },
  lineLabelRest: {
    flex: 1,
    fontSize: 13.5,
    color: '#d1d5db',
  },
};
