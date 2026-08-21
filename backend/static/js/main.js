/**
 * ExplainX — Frontend Engine
 */

/* ═══ STATE ═════════════════════════════════════════════════════════════════ */
const state = {
  mode:               "beginner",
  language:           "python",
  comprehensionScore: 50,
  currentExplanation: "",
  isSpeaking:         false,
};

const LOADING_MSGS = [
  "Parsing code structure…",
  "Generating your explanation…",
  "Crafting the narrative…",
  "Analysing complexity…",
  "Polishing the explanation…",
];

const MODE_LABELS = {
  beginner:  "🌱 Beginner",
  technical: "⚙️ Technical",
  interview: "🎯 Interview",
  story:     "📖 Story",
  adaptive:  "✨ Adaptive",
};

const SAMPLE_CODES = {
  python: `def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

nums = [1, 3, 5, 7, 9, 11, 13]
result = binary_search(nums, 7)
print(f"Found at index: {result}")`,

  javascript: `function mergeSort(arr) {
  if (arr.length <= 1) return arr;
  const mid   = Math.floor(arr.length / 2);
  const left  = mergeSort(arr.slice(0, mid));
  const right = mergeSort(arr.slice(mid));
  return merge(left, right);
}

function merge(left, right) {
  const result = [];
  let i = 0, j = 0;
  while (i < left.length && j < right.length) {
    if (left[i] <= right[j]) result.push(left[i++]);
    else result.push(right[j++]);
  }
  return result.concat(left.slice(i)).concat(right.slice(j));
}`,

  java: `public class FibonacciDP {
    public static int fib(int n) {
        if (n <= 1) return n;
        int[] dp = new int[n + 1];
        dp[0] = 0; dp[1] = 1;
        for (int i = 2; i <= n; i++) {
            dp[i] = dp[i-1] + dp[i-2];
        }
        return dp[n];
    }
}`,
};

/* ═══ DOM REFS ══════════════════════════════════════════════════════════════ */
const $ = id => document.getElementById(id);
const els = {
  codeInput:         $("codeInput"),
  langSelect:        $("langSelect"),
  modePills:         $("modePills"),
  btnExplain:        $("btnExplain"),
  btnModeLabel:      $("btnModeLabel"),
  btnClear:          $("btnClear"),
  btnSample:         $("btnSample"),
  btnReset:          $("btnReset"),
  btnBlocks:         $("btnBlocks"),
  btnCollapseAll:    $("btnCollapseAll"),
  lineNumbers:       $("lineNumbers"),
  editorFilename:    $("editorFilename"),
  structureTags:     $("structureTags"),

  outputPlaceholder: $("outputPlaceholder"),
  outputLoading:     $("outputLoading"),
  outputContent:     $("outputContent"),
  blocksContent:     $("blocksContent"),
  loadingText:       $("loadingText"),
  blocksList:        $("blocksList"),
  blocksTitle:       $("blocksTitle"),

  modeBadge:         $("modeBadge"),
  complexityChips:   $("complexityChips"),
  explanationBody:   $("explanationBody"),
  lineBreakdown:     $("lineBreakdown"),
  questionsSection:  $("questionsSection"),

  meterBar:          $("meterBar"),
  meterScore:        $("meterScore"),

  lineTooltip:       $("lineTooltip"),
  tooltipLineNum:    $("tooltipLineNum"),
  tooltipCode:       $("tooltipCode"),
  tooltipBody:       $("tooltipBody"),
  tooltipClose:      $("tooltipClose"),

  btnVoice:          $("btnVoice"),
  btnVoiceStop:      $("btnVoiceStop"),

  feedbackToast:     $("feedbackToast"),
  toastMsg:          $("toastMsg"),

  chatMessages:      $("chatMessages"),
  chatInput:         $("chatInput"),
  btnChatSend:       $("btnChatSend"),
  btnClearChat:      $("btnClearChat"),
};

/* ═══ INIT ══════════════════════════════════════════════════════════════════ */
document.addEventListener("DOMContentLoaded", () => {
  loadSession();
  bindEvents();
  updateLineNumbers();
});

function bindEvents() {
  els.modePills.querySelectorAll(".mode-pill").forEach(btn => {
    btn.addEventListener("click", () => {
      state.mode = btn.dataset.mode;
      els.modePills.querySelectorAll(".mode-pill").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      els.btnModeLabel.textContent = btn.textContent.replace(/[🌱⚙️🎯📖✨]/u, "").trim();
    });
  });

  els.langSelect.addEventListener("change", () => {
    state.language = els.langSelect.value;
    const ext = { python:"py", javascript:"js", typescript:"ts", java:"java", cpp:"cpp", c:"c" };
    els.editorFilename.textContent = `untitled.${ext[state.language] || state.language}`;
  });

  els.codeInput.addEventListener("input",   updateLineNumbers);
  els.codeInput.addEventListener("keydown", handleTabKey);
  els.codeInput.addEventListener("scroll",  syncScroll);

  els.btnExplain.addEventListener("click",     runExplain);
  els.btnBlocks.addEventListener("click",      runBlockExplain);
  els.btnClear.addEventListener("click",       clearEditor);
  els.btnSample.addEventListener("click",      loadSample);
  els.btnReset.addEventListener("click",       resetSession);
  els.tooltipClose.addEventListener("click",   hideTooltip);
  els.btnCollapseAll.addEventListener("click", () =>
    document.querySelectorAll(".block-card").forEach(c => c.classList.remove("expanded"))
  );

  els.btnVoice.addEventListener("click",     startTTS);
  els.btnVoiceStop.addEventListener("click", stopTTS);

  document.addEventListener("click", e => {
    const item = e.target.closest(".line-item");
    if (item) fetchLineExplanation(Number(item.dataset.line));
  });

  els.btnChatSend.addEventListener("click", sendChatMessage);
  els.btnClearChat.addEventListener("click", clearChat);
  els.chatInput.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendChatMessage(); }
  });

  document.querySelectorAll(".qa-btn").forEach(btn => {
    btn.addEventListener("click", () => sendQuickAction(btn.dataset.action, btn));
  });
}

/* ═══ FULL EXPLAIN ══════════════════════════════════════════════════════════ */
async function runExplain() {
  const code = els.codeInput.value.trim();
  if (!code) { showToast("⚠️ Please paste some code first!"); return; }

  setOutputState("loading");
  cycleLoadingMsg();
  els.btnExplain.disabled = true;

  try {
    const res  = await fetch("/api/explain", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, mode: state.mode, language: state.language }),
    });
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();
    if (data.error) throw new Error(data.error);

    state.currentExplanation = data.explanation || "";
    renderExplanation(data);
    setOutputState("content");
    clearChat();

    if (data.adaptive_resolved) showToast(`✨ Adaptive → ${MODE_LABELS[data.mode_used]}`);
  } catch (err) {
    console.error(err);
    setOutputState("placeholder");
    showToast("❌ " + err.message);
  } finally {
    els.btnExplain.disabled = false;
  }
}

/* ═══ BLOCK-BY-BLOCK ════════════════════════════════════════════════════════ */
async function runBlockExplain() {
  const code = els.codeInput.value.trim();
  if (!code) { showToast("⚠️ Please paste some code first!"); return; }

  els.btnBlocks.disabled = true;
  els.btnBlocks.innerHTML = `<span>⏳</span><span>Splitting & Explaining…</span>`;
  setOutputState("blocks");
  els.blocksList.innerHTML = "";
  els.blocksTitle.textContent = "Splitting code into blocks…";

  try {
    const res  = await fetch("/api/explain-blocks", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, mode: state.mode, language: state.language }),
    });
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();
    if (data.error) throw new Error(data.error);

    els.blocksTitle.textContent =
      `🧩 ${data.total} Block${data.total !== 1 ? "s" : ""} — ${MODE_LABELS[data.mode_used] || data.mode_used} Mode`;
    data.blocks.forEach(renderBlockCard);

  } catch (err) {
    console.error(err);
    setOutputState("placeholder");
    showToast("❌ " + err.message);
  } finally {
    els.btnBlocks.disabled = false;
    els.btnBlocks.innerHTML = `<span>🧩</span><span>Explain Block by Block</span><span class="btn-blocks-hint">great for long code</span>`;
  }
}

function renderBlockCard(block) {
  const card      = document.createElement("div");
  card.className  = "block-card";
  card.id         = `block-${block.index}`;

  const range      = `Lines ${block.start_line}–${block.end_line} · ${block.line_count} line${block.line_count !== 1 ? "s" : ""}`;
  const conceptHtml = block.key_concept
    ? `<span class="block-concept">${escHtml(block.key_concept)}</span>` : "";
  const exHtml = window.marked ? marked.parse(block.explanation || "") : (block.explanation || "");

  card.innerHTML = `
    <div class="block-header" onclick="toggleBlock(${block.index})">
      <span class="block-num">${block.index}</span>
      <div class="block-meta">
        <div class="block-title">${escHtml(block.summary || block.title)}</div>
        <div class="block-subtitle">${range}</div>
      </div>
      ${conceptHtml}
      <span class="block-toggle">▼</span>
    </div>
    <div class="block-body">
      <div class="block-code-wrap">
        <pre><code class="language-${state.language}">${escHtml(block.code)}</code></pre>
      </div>
      <div class="block-explanation">${exHtml}</div>
    </div>`;

  els.blocksList.appendChild(card);
  card.querySelectorAll("pre code").forEach(b => hljs.highlightElement(b));
  if (block.index === 1) card.classList.add("expanded");
}

window.toggleBlock = index => {
  document.getElementById(`block-${index}`)?.classList.toggle("expanded");
};

/* ═══ RENDER EXPLANATION ════════════════════════════════════════════════════ */
function renderExplanation(data) {
  els.modeBadge.textContent = MODE_LABELS[data.mode_used] || data.mode_used;

  // Complexity chips
  els.complexityChips.innerHTML = "";
  const c = data.complexity || {};
  if (c.time)    els.complexityChips.innerHTML += chip("Time",    c.time);
  if (c.space)   els.complexityChips.innerHTML += chip("Space",   c.space);
  if (c.pattern) els.complexityChips.innerHTML += chip("Pattern", c.pattern);

  // Main explanation
  els.explanationBody.innerHTML = window.marked
    ? marked.parse(data.explanation || "")
    : (data.explanation || "");
  els.explanationBody.querySelectorAll("pre code").forEach(b => hljs.highlightElement(b));

  // Line breakdown — clean, no brackets or quotes
  renderLineBreakdown(data.line_explanations || [], data.code || els.codeInput.value);

  // Questions
  renderQuestions(data.questions || [], data.mode_used);

  // Structure tags
  renderStructureTags(data.structure || {});
}

function chip(label, value) {
  return `<span class="chip"><strong>${label}:</strong> ${escHtml(String(value))}</span>`;
}

/* ── Line Breakdown — clean card layout, no raw code ─────────────────────── */
function renderLineBreakdown(lines, fullCode) {
  if (!lines.length) { els.lineBreakdown.innerHTML = ""; return; }

  const codeLines = (fullCode || els.codeInput.value || "").split("\n");

  const header = `<p class="line-breakdown-title">📄 Line-by-Line Notes
    <small>(click any line to deep-dive)</small></p>`;

  const items = lines.map(l => {
    // Get the actual source line — clean it up, no quotes or brackets
    const sourceLine = (codeLines[l.line - 1] || "").trim();
    const note       = (l.note || "").replace(/[{}"'[\]]/g, "").trim();

    return `
      <div class="line-item" data-line="${l.line}">
        <span class="line-badge">Line ${l.line}</span>
        <div class="line-content">
          <span class="line-source">${escHtml(sourceLine)}</span>
          <span class="line-note-text">${escHtml(note)}</span>
        </div>
        <span class="line-arrow">›</span>
      </div>`;
  }).join("");

  els.lineBreakdown.innerHTML = header + `<div class="line-list">${items}</div>`;
}

function renderQuestions(questions, mode) {
  if (!questions.length) { els.questionsSection.innerHTML = ""; return; }
  const qs = questions.map((q, i) => `
    <div class="question-item" id="q${i}">
      <span class="question-text">💬 ${escHtml(q)}</span>
      <div class="question-btns">
        <button class="q-btn yes" onclick="handleFeedback(${i},'yes','${mode}')">✓ Got it</button>
        <button class="q-btn no"  onclick="handleFeedback(${i},'no','${mode}')">✗ Confused</button>
      </div>
    </div>`).join("");
  els.questionsSection.innerHTML = `<div class="questions-title">🧠 Check Your Understanding</div>${qs}`;
}

function renderStructureTags(structure) {
  const tags = [];
  (structure.functions  || []).forEach(f => tags.push({ type:"fn",   text:`fn: ${f.name}` }));
  (structure.classes    || []).forEach(c => tags.push({ type:"cls",  text:`class: ${c.name}` }));
  (structure.loops      || []).forEach(l => tags.push({ type:"loop", text:`${l.type} loop` }));
  structure.recursion && tags.push({ type:"rec", text:"recursive" });
  const unique = [...new Map(tags.map(t => [t.text, t])).values()];
  els.structureTags.innerHTML = unique.slice(0, 8).map(t =>
    `<span class="struct-tag ${t.type}">${escHtml(t.text)}</span>`
  ).join("");
}

/* ═══ FOLLOW-UP CHAT ════════════════════════════════════════════════════════ */
async function sendChatMessage() {
  const msg = els.chatInput.value.trim();
  if (!msg) return;
  if (!state.currentExplanation) { showToast("⚠️ Generate an explanation first!"); return; }
  els.chatInput.value = "";
  appendUserBubble(msg);
  await callFollowup({ message: msg });
}

async function sendQuickAction(action, btnEl) {
  if (!state.currentExplanation) { showToast("⚠️ Generate an explanation first!"); return; }
  document.querySelectorAll(".qa-btn").forEach(b => b.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");
  const labels = {
    simpler:"🐣 Explain simpler", eli5:"👶 Explain like I'm 5",
    analogy:"🌍 Real-world analogy", example:"📌 Show an example",
    visualize:"🔍 Visualize it", deeper:"🚀 Go deeper",
    mistakes:"⚠️ Common mistakes", compare:"⚖️ Compare approaches", summary:"📋 Short summary",
  };
  appendUserBubble(labels[action] || action, true);
  await callFollowup({ action });
  setTimeout(() => { if (btnEl) btnEl.classList.remove("active"); }, 1200);
}

async function callFollowup({ message = "", action = null }) {
  const code = els.codeInput.value.trim();
  setQABtnsDisabled(true);
  els.btnChatSend.disabled = true;
  const typingEl = appendTypingIndicator();
  try {
    const res = await fetch("/api/followup", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message, action, code, language: state.language,
        current_explanation: state.currentExplanation,
      }),
    });
    typingEl.remove();
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    appendBotBubble(data.reply, data.suggestion);
  } catch (err) {
    typingEl.remove();
    appendBotBubble(`❌ Sorry, something went wrong: ${err.message}`);
  } finally {
    setQABtnsDisabled(false);
    els.btnChatSend.disabled = false;
  }
}

function appendUserBubble(text) {
  const div = document.createElement("div");
  div.className = "chat-msg chat-msg-user";
  div.innerHTML = `<span class="chat-label">You</span><div class="chat-bubble">${escHtml(text)}</div>`;
  els.chatMessages.appendChild(div);
  scrollChat();
}

function appendBotBubble(markdown, suggestion = null) {
  const div  = document.createElement("div");
  div.className = "chat-msg chat-msg-bot";
  const html = window.marked ? marked.parse(markdown || "") : escHtml(markdown || "");
  const suggHtml = suggestion
    ? `<button class="chat-suggestion" onclick="sendQuickAction('${suggestion.action}',null)">${escHtml(suggestion.label)}</button>`
    : "";
  div.innerHTML = `<span class="chat-label">ExplainX</span><div class="chat-bubble">${html}</div>${suggHtml}`;
  els.chatMessages.appendChild(div);
  div.querySelectorAll("pre code").forEach(b => hljs.highlightElement(b));
  scrollChat();
}

function appendTypingIndicator() {
  const div = document.createElement("div");
  div.className = "chat-msg chat-msg-bot";
  div.innerHTML = `<span class="chat-label">ExplainX</span>
    <div class="chat-typing">
      <span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>
    </div>`;
  els.chatMessages.appendChild(div);
  scrollChat();
  return div;
}

function scrollChat() { els.chatMessages.scrollTop = els.chatMessages.scrollHeight; }
function clearChat()  { els.chatMessages.innerHTML = ""; }
function setQABtnsDisabled(v) { document.querySelectorAll(".qa-btn").forEach(b => b.disabled = v); }

/* ═══ LINE TOOLTIP ══════════════════════════════════════════════════════════ */
async function fetchLineExplanation(lineNum) {
  const code  = els.codeInput.value;
  const lines = code.split("\n");
  if (lineNum < 1 || lineNum > lines.length) return;

  els.tooltipLineNum.textContent = `Line ${lineNum}`;
  els.tooltipCode.textContent    = lines[lineNum - 1].trim().substring(0, 50);
  els.tooltipBody.textContent    = "Generating…";
  els.lineTooltip.classList.remove("hidden");

  try {
    const res  = await fetch("/api/line-explain", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, line: lineNum, mode: state.mode, language: state.language }),
    });
    const data = await res.json();
    // Clean up any stray brackets from explanation
    const clean = (data.explanation || "No explanation available.").replace(/[{}"'[\]]/g, "");
    els.tooltipBody.textContent = clean;
    if (data.concept) {
      els.tooltipBody.innerHTML +=
        `<br><br><strong style="color:var(--teal);font-size:.75rem;">💡 ${escHtml(data.concept)}</strong>`;
    }
  } catch { els.tooltipBody.textContent = "Could not load explanation."; }
}

function hideTooltip() { els.lineTooltip.classList.add("hidden"); }

/* ═══ TTS ════════════════════════════════════════════════════════════════════ */
function startTTS() {
  if (!state.currentExplanation) return;
  if (!("speechSynthesis" in window)) { showToast("🔇 Speech synthesis not supported."); return; }
  stopTTS();
  const u   = new SpeechSynthesisUtterance(els.explanationBody.textContent.substring(0, 3000));
  u.rate    = 0.92; u.pitch = 1;
  u.onend   = () => { els.btnVoice.classList.remove("hidden"); els.btnVoiceStop.classList.add("hidden"); state.isSpeaking = false; };
  window.speechSynthesis.speak(u);
  state.isSpeaking = true;
  els.btnVoice.classList.add("hidden");
  els.btnVoiceStop.classList.remove("hidden");
}
function stopTTS() {
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  state.isSpeaking = false;
  els.btnVoice.classList.remove("hidden");
  els.btnVoiceStop.classList.add("hidden");
}

/* ═══ EDITOR ════════════════════════════════════════════════════════════════ */
function updateLineNumbers() {
  els.lineNumbers.textContent = (els.codeInput.value || "").split("\n").map((_, i) => i + 1).join("\n");
}
function handleTabKey(e) {
  if (e.key === "Tab") {
    e.preventDefault();
    const s = els.codeInput.selectionStart, end = els.codeInput.selectionEnd;
    els.codeInput.value = els.codeInput.value.substring(0, s) + "    " + els.codeInput.value.substring(end);
    els.codeInput.selectionStart = els.codeInput.selectionEnd = s + 4;
  }
}
function syncScroll() { els.lineNumbers.scrollTop = els.codeInput.scrollTop; }
function clearEditor() {
  els.codeInput.value = ""; updateLineNumbers();
  els.structureTags.innerHTML = "";
  setOutputState("placeholder"); hideTooltip(); clearChat();
}
function loadSample() {
  els.codeInput.value = SAMPLE_CODES[state.language] || SAMPLE_CODES.python;
  updateLineNumbers();
  showToast(`✅ Loaded ${state.language} sample`);
}

/* ═══ SESSION ════════════════════════════════════════════════════════════════ */
async function loadSession() {
  try {
    const data = await (await fetch("/api/session")).json();
    state.comprehensionScore = data.comprehension_score || 50;
    updateMeter(state.comprehensionScore);
    if (data.last_mode) {
      state.mode = data.last_mode;
      els.modePills.querySelectorAll(".mode-pill").forEach(b => {
        const on = b.dataset.mode === data.last_mode;
        b.classList.toggle("active", on);
        if (on) els.btnModeLabel.textContent = b.textContent.replace(/[🌱⚙️🎯📖✨]/u, "").trim();
      });
    }
  } catch {}
}
async function resetSession() {
  await fetch("/api/reset", { method: "POST" });
  state.comprehensionScore = 50; updateMeter(50); clearChat();
  showToast("🔄 Session reset");
}

/* ═══ UI HELPERS ════════════════════════════════════════════════════════════ */
function setOutputState(s) {
  els.outputPlaceholder.classList.toggle("hidden", s !== "placeholder");
  els.outputLoading.classList.toggle("hidden",     s !== "loading");
  els.outputContent.classList.toggle("hidden",     s !== "content");
  els.blocksContent.classList.toggle("hidden",     s !== "blocks");
}
function updateMeter(score) {
  els.meterBar.style.width   = `${score}%`;
  els.meterScore.textContent = score;
  const color = score < 30 ? "#ff6b4a" : score < 70 ? "#ffb432" : "#3dd9c0";
  els.meterBar.style.background = `linear-gradient(90deg,${color}cc,${color})`;
}
function showToast(msg) {
  els.toastMsg.textContent = msg;
  els.feedbackToast.classList.remove("hidden");
  els.feedbackToast.classList.add("show");
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => {
    els.feedbackToast.classList.remove("show");
    setTimeout(() => els.feedbackToast.classList.add("hidden"), 400);
  }, 2800);
}
function cycleLoadingMsg() {
  let i = 0;
  clearInterval(cycleLoadingMsg._iv);
  cycleLoadingMsg._iv = setInterval(() => {
    els.loadingText.textContent = LOADING_MSGS[i++ % LOADING_MSGS.length];
  }, 900);
  setTimeout(() => clearInterval(cycleLoadingMsg._iv), 15000);
}
function escHtml(s) {
  return (s || "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

/* Feedback handler */
window.handleFeedback = async function(qi, answer, mode) {
  const correct    = answer === "yes";
  const difficulty = mode === "interview" ? "hard" : mode === "technical" ? "medium" : "easy";
  document.getElementById(`q${qi}`)?.querySelectorAll(".q-btn").forEach(b => b.disabled = true);
  try {
    const res  = await fetch("/api/feedback", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ correct, difficulty }),
    });
    const data = await res.json();
    state.comprehensionScore = data.new_score;
    updateMeter(data.new_score);
    showToast(data.message);
    if (data.recommended_mode !== state.mode)
      setTimeout(() => showToast(`💡 Try ${MODE_LABELS[data.recommended_mode]} mode!`), 1800);
  } catch(e) { console.error(e); }
};