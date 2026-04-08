"""
ExplainX Explanation Engine - Groq Backend
"""

import os, json, re
from groq import Groq, APIConnectionError
from typing import Dict, Any, List, Optional

MODEL  = "llama-3.3-70b-versatile"


class ExplainXEngine:
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY is not set. Add this to your .env or environment variables."
            )

        self.client = Groq(api_key=api_key)
        self.model  = os.environ.get("GROQ_MODEL", MODEL)

    # ── Base persona per mode ─────────────────────────────────────────────────
    MODE_PROMPTS = {
        "beginner": """You are ExplainX — a beginner-friendly code explanation engine.
Your tone is simple, warm, and encouraging.
You explain code like writing neat study notes for a student seeing it for the first time.""",

        "technical": """You are ExplainX — a technical code explanation engine.
Your tone is precise, concise, and professional.
You explain code like a senior engineer writing internal documentation.""",

        "interview": """You are ExplainX — an interview-prep code explanation engine.
Your tone is sharp and analytical.
You explain code like a FAANG interviewer walking through a solution.""",

        "story": """You are ExplainX — a creative code explanation engine.
Your tone is vivid and narrative.
You explain code by casting it as a story — variables are characters, loops are journeys.""",
    }

    # ── Strict format rules injected into every prompt ────────────────────────
    STRUCTURE_FORMAT_RULES = {
        "beginner": """
==================================================
STRICT OUTPUT FORMAT — follow exactly, no exceptions
==================================================

You must explain the code using this exact structure:

## 🔍 What This Code Does
Write 1 sentence only. Plain English. No jargon.

--------------------------------------------------

## 🧩 Line-by-Line Explanation

For EVERY meaningful line write:

Line <number>: <exact code from that line>
Explanation: <one clear sentence — what this line does>

If a line has important keywords also add:
IMPORTANT: <keyword> → <what it means>

Separate each line block with:
--------------------------------------------------

## 💡 Key Takeaways
- Write 3 to 5 bullet points
- Each bullet = one important concept
- One sentence per bullet
- Use IMPORTANT: <term> → <meaning> for key terms

==================================================
STRICT RULES — never break these:
- NO paragraphs anywhere. Every section uses lists or line-by-line entries.
- NO quotation marks around code lines.
- NO curly brackets or square brackets in explanations.
- NO long sentences. Maximum 15 words per explanation line.
- Use | to separate multiple ideas on one line.
- Use **bold** only for key terms.
- Keep spacing clean. One blank line between each entry.
==================================================
""",

        "technical": """
==================================================
STRICT OUTPUT FORMAT — follow exactly, no exceptions
==================================================

## ⚡ Summary
One sentence. What does this code do?

--------------------------------------------------

## 🔬 Line-by-Line Breakdown

For EVERY meaningful line write:

Line <number>: <exact code from that line>
Explanation: <precise technical explanation>
IMPORTANT: <keyword> → <technical meaning>   ← only if line has a key term

Separate each line block with:
--------------------------------------------------

## ⚠️ Edge Cases
- Bullet list only
- One issue per bullet
- One sentence each

--------------------------------------------------

## 🛠 Best Practices
- Bullet list only
- One recommendation per bullet

==================================================
STRICT RULES:
- NO paragraphs. Line-by-line entries and bullet lists only.
- NO quotation marks or stray brackets in explanations.
- Use `code` formatting for all variable names and keywords.
- Maximum 20 words per explanation line.
- Use | to separate multiple technical points on one line.
==================================================
""",

        "interview": """
==================================================
STRICT OUTPUT FORMAT — follow exactly, no exceptions
==================================================

## 📌 What It Does
One sentence.

--------------------------------------------------

## ⏱ Complexity
- Time: O(?) — reason in one sentence
- Space: O(?) — reason in one sentence

--------------------------------------------------

## 🧩 Line-by-Line Walkthrough

For EVERY meaningful line write:

Line <number>: <exact code from that line>
Explanation: <what this line does in the algorithm>
IMPORTANT: <keyword> → <algorithmic meaning>   ← only if relevant

Separate each line block with:
--------------------------------------------------

## 🚀 Optimizations
1. First improvement — one sentence
2. Second improvement — one sentence

==================================================
STRICT RULES:
- NO paragraphs. Structured entries only.
- NO quotation marks or stray brackets.
- Use `code` for all identifiers.
- Maximum 20 words per explanation line.
==================================================
""",

        "story": """
==================================================
STRICT OUTPUT FORMAT — follow exactly, no exceptions
==================================================

## 📖 The Story
Write 3 short sentences only. Each sentence on its own line.
Make it vivid — variables are characters, loops are journeys, functions are missions.

--------------------------------------------------

## 🗺 Scene by Scene

For EVERY meaningful line write:

Line <number>: <exact code from that line>
Story Beat: <one sentence mapping this line to the story>

Separate each entry with:
--------------------------------------------------

## 🎭 The Cast
- <variable or function name> → <their role in the story>
- One bullet per character

--------------------------------------------------

## 🌟 The Moral
One sentence. The core lesson.

==================================================
STRICT RULES:
- NO paragraphs. Short entries only.
- NO quotation marks or stray brackets.
- Maximum 15 words per story beat.
- Keep the narrative fun and memorable.
==================================================
""",
    }

    # ── Follow-up quick actions ───────────────────────────────────────────────
    FOLLOWUP_ACTIONS = {
        "simpler":   "Re-explain this code in the simplest possible way. Use a 5-year-old level analogy. Short sentences only. Bullet points or numbered list — no paragraphs.",
        "eli5":      "Explain this like I am 5 years old. Use a fun story or toy analogy. Maximum 5 short sentences. No paragraphs.",
        "analogy":   "Give one real-world analogy — not tech-related — that maps perfectly to what this code does. Bullet points. No paragraphs.",
        "example":   "Show a concrete real-world example of when someone would use this code. Use a numbered list. No paragraphs.",
        "deeper":    "Go deeper on the advanced concepts and trade-offs. Use bullet points and short numbered lists. No paragraphs.",
        "visualize": "Walk through what happens step-by-step in memory when this code runs. Use a numbered list — one step per item. No paragraphs.",
        "mistakes":  "List the most common mistakes beginners make with this type of code. Use a numbered list. One mistake per item. No paragraphs.",
        "compare":   "Compare this approach with 1 or 2 alternatives. Use a bullet list with pros and cons. No paragraphs.",
        "summary":   "Give a 3 to 4 bullet point summary of what this code does. Plain English. No jargon. No paragraphs.",
    }

    # ── Full Explanation ──────────────────────────────────────────────────────

    def explain(self, code, mode, language, structure, line_focus, comprehension_score):
        system = self.MODE_PROMPTS.get(mode, self.MODE_PROMPTS["beginner"])
        prompt = self._build_explain_prompt(code, language, structure, line_focus, comprehension_score, mode)
        text   = self._call_groq(system, prompt)
        parsed = self._parse_ai_response(text)
        return {
            "explanation": parsed.get("explanation", text),
        }

    # ── Follow-up ─────────────────────────────────────────────────────────────

    def followup(self, code, language, current_explanation, message,
                 action, chat_history, comprehension_score):
        if action and action in self.FOLLOWUP_ACTIONS:
            user_message = self.FOLLOWUP_ACTIONS[action]
        else:
            user_message = message

        system_prompt = """You are ExplainX — a helpful code explanation assistant.

STRICT RULES for every reply:
- Use bullet points or numbered lists. Never long paragraphs.
- No quotation marks around code. No stray brackets in explanations.
- Keep each point to one clear sentence.
- Maximum 15 words per bullet or list item.
- Use IMPORTANT: <term> → <meaning> for key terms.
- End with one short encouraging sentence if the user seemed confused."""

        history_text = ""
        if chat_history:
            history_text = "\n\nPrevious conversation:\n"
            for turn in chat_history[-6:]:
                role = "User" if turn["role"] == "user" else "ExplainX"
                history_text += f"{role}: {turn['content']}\n"

        user_prompt = f"""The user is learning about this {language} code:

```{language}
{code[:800]}{"..." if len(code) > 800 else ""}
```

Previous explanation summary:
{current_explanation[:300]}{"..." if len(current_explanation) > 300 else ""}
{history_text}

Comprehension score: {comprehension_score}/100
User request: {user_message}

Reply using bullet points or a numbered list. No paragraphs. No quotation marks."""

        reply      = self._call_groq(system_prompt, user_prompt)
        suggestion = self._suggest_next_action(action, comprehension_score)
        return {"reply": reply, "suggestion": suggestion}

    # ── Block-by-Block ────────────────────────────────────────────────────────

    def explain_blocks(self, blocks, mode, language):
        results = []
        system  = self.MODE_PROMPTS.get(mode, self.MODE_PROMPTS["beginner"])

        for block in blocks:
            prompt = f"""Explain this {language} code block in {mode} mode.

Block {block['index']}: {block['title']} (lines {block['start_line']} to {block['end_line']})

```{language}
{block['code']}
```

Use this format:
- One-line summary (what this block does)
- Then bullet points: 3 to 5 points, one sentence each
- No paragraphs. No quotation marks. No stray brackets.
- Use IMPORTANT: term → meaning for key terms.
- Identify the single most important concept in 3-5 words.

Return ONLY this JSON:
{{
  "summary": "<one-line heading, no quotes>",
  "explanation": "<bullet point markdown — no paragraphs, no quotation marks>",
  "key_concept": "<3 to 5 word concept>"
}}"""

            try:
                text   = self._call_groq(system, prompt)
                parsed = self._parse_ai_response(text)
                results.append(parsed.get("explanation", text))
            except Exception as e:
                results.append(f"Error: {e}")
        return results

    # ── Single Line ───────────────────────────────────────────────────────────

    def explain_line(self, code, line_num, mode, language):
        lines = code.split("\n")
        if line_num < 1 or line_num > len(lines):
            return {"error": "Line number out of range"}

        target    = lines[line_num - 1]
        ctx_start = max(0, line_num - 4)
        ctx_end   = min(len(lines), line_num + 3)
        context   = "\n".join(lines[ctx_start:ctx_end])
        system    = self.MODE_PROMPTS.get(mode, self.MODE_PROMPTS["beginner"])
        prompt    = f"""Explain line {line_num} of this {language} code.

Context:
```{language}
{context}
```

The specific line: {target.strip()}

Use this format:
Line {line_num}: {target.strip()}
Explanation: <one clear sentence — what this line does>
IMPORTANT: <keyword> → <what it means>   (only if there is a key term)

Rules:
- No quotation marks. No brackets in the explanation.
- Maximum 15 words in the explanation.
- Plain English only.

Return ONLY this JSON:
{{"line": {line_num}, "code": "{target.strip()}", "explanation": "<explanation>", "concept": "<3-5 word concept>"}}"""

        text = self._call_groq(system, prompt)
        try:
            result = self._extract_json(text)
            if isinstance(result, dict):
                result["explanation"] = re.sub(r'[{}\[\]"\'`]', '', result.get("explanation", "")).strip()
                return {"explanation": result.get("explanation"), "concept": result.get("concept")}
            return {"explanation": text, "concept": ""}
        except Exception:
            clean = re.sub(r'[{}\[\]"\'`]', '', text).strip()
            return {"explanation": clean, "concept": ""}

    # ── Adaptive ──────────────────────────────────────────────────────────────

    def resolve_adaptive_mode(self, score):
        if score < 55:  return "beginner"
        if score < 85:  return "technical"
        return "interview"

    # ── Prompt Builder ────────────────────────────────────────────────────────

    def _build_explain_prompt(self, code, language, structure, line_focus, score, mode):
        parts = []
        if structure.get("functions"):
            parts.append(f"Functions: {', '.join(f['name'] for f in structure['functions'])}")
        if structure.get("loops"):
            parts.append(f"Loops: {len(structure['loops'])}")
        if structure.get("conditionals"):
            parts.append(f"Conditionals: {len(structure['conditionals'])}")
        if structure.get("recursion"):
            parts.append("Uses recursion")
        if structure.get("classes"):
            parts.append(f"Classes: {', '.join(c['name'] for c in structure['classes'])}")

        line_note = ""
        if line_focus:
            ls = code.split("\n")
            if 1 <= line_focus <= len(ls):
                line_note = f"\nPay special attention to line {line_focus}: {ls[line_focus-1].strip()}"

        fmt = self.STRUCTURE_FORMAT_RULES.get(mode, self.STRUCTURE_FORMAT_RULES["beginner"])

        return f"""Explain this {language} code.
Detected: {'; '.join(parts) or 'simple code'} | Learner score: {score}/100{line_note}

```{language}
{code}
```

{fmt}

IMPORTANT OUTPUT RULES:
- No quotation marks anywhere in the explanation text.
- No curly brackets or square brackets in explanation text.
- No long paragraphs — use the line-by-line format and bullet points only.
- Clean spacing between each entry.

Return ONLY a JSON object with no markdown fences wrapping it:
{{
  "explanation": "<your full structured explanation following the format above>",
  "line_explanations": [
    {{"line": 1, "note": "<plain English — what this line does — no quotes or brackets>"}}
  ],
  "complexity": {{
    "time": "<O notation and one-sentence reason>",
    "space": "<O notation and one-sentence reason>",
    "pattern": "<algorithm pattern name>"
  }}
}}"""

    # ── Internal Helpers ──────────────────────────────────────────────────────

    def _suggest_next_action(self, current_action, score):
        if current_action in ("simpler", "eli5") and score < 40:
            return {"action": "analogy", "label": "🎯 Try a real-world analogy"}
        if current_action == "analogy":
            return {"action": "example", "label": "📌 See a concrete example"}
        if current_action == "example":
            return {"action": "visualize", "label": "🔍 Visualize step-by-step"}
        if score > 70 and current_action not in ("deeper", "compare"):
            return {"action": "deeper", "label": "🚀 Go deeper"}
        return None

    def _call_groq(self, system, user):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
            )
            return response.choices[0].message.content

        except APIConnectionError as conn_err:
            raise ConnectionError(
                "Could not connect to Groq API. Check network, DNS, and GROQ endpoint settings. "
                f"Original: {conn_err}"
            ) from conn_err
        except OSError as os_err:
            raise ConnectionError(
                "Network error while calling Groq API. Ensure internet access and correct proxy settings. "
                f"Original: {os_err}"
            ) from os_err

    def _extract_json(self, text):
        try:
            return json.loads(text.strip())
        except Exception:
            pass
        clean = re.sub(r"^```(?:json)?\n?", "", text.strip())
        clean = re.sub(r"\n?```$", "", clean).strip()
        try:
            return json.loads(clean)
        except Exception:
            pass
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return text

    def _parse_ai_response(self, text):
        result = self._extract_json(text)
        if isinstance(result, dict):
            return result
        try:
            parsed = json.loads(result)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
        return {"explanation": text, "line_explanations": [], "complexity": {}}

    def _extract_highlights(self, structure):
        highlights = []
        for fn   in structure.get("functions",    []):
            highlights.append({"line": fn["line"],   "type": "function",  "label": fn["name"]})
        for loop in structure.get("loops",        []):
            highlights.append({"line": loop["line"], "type": "loop",      "label": loop["type"] + " loop"})
        for cond in structure.get("conditionals", []):
            highlights.append({"line": cond["line"], "type": "condition", "label": "conditional"})
        return highlights