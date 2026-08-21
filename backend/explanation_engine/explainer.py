"""
LineByLine & ExplainX Explanation Engine - Gemini Backend
"""

from google import genai
import os, json, re
from typing import Dict, Any, List, Optional

try:
    import google.genai
    import google.genai.types as types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

MODEL = "gemini-3.6-flash"

class ExplainXEngine:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GROQ_API_KEY")
        self.model = os.environ.get("GEMINI_MODEL", MODEL)
        if HAS_GENAI and api_key and api_key != "your_gemini_api_key_here":
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None

    # ── Four Locked Personas ──────────────────────────────────────────────────
    MODE_PROMPTS = {
        "academic": """You are LineByLine — an academic computer science tutor.
Your tone is clear, structured, precise, and educational.
You explain code like writing neat study notes for a CS student.""",

        "beginner": """You are LineByLine — an academic computer science tutor.
Your tone is clear, structured, precise, and educational.
You explain code like writing neat study notes for a CS student.""",

        "story": """You are LineByLine — a creative story-based code tutor.
Your tone is vivid, narrative, and engaging.
You explain code by casting it as a story — variables are characters, loops are journeys, functions are missions.""",

        "interview": """You are LineByLine — an interview-prep code tutor.
Your tone is sharp, analytical, and performance-focused.
You explain code like a FAANG interviewer walking through algorithmic efficiency and trade-offs.""",

        "toddler": """You are LineByLine — a toddler-friendly ELI5 code tutor.
Your tone is playful, warm, and ultra-simple.
You explain code like you are talking to a 5-year-old child using toy, food, or playground analogies with no jargon.""",
    }

    # ── Format rules ──────────────────────────────────────────────────────────
    STRUCTURE_FORMAT_RULES = {
        "academic": """
## 🔍 What This Code Does
Write 1 sentence only. Plain English. No jargon.

## 🧩 Line-by-Line Explanation
For EVERY line write:
Line <number>: <exact code>
Explanation: <one clear sentence>

## 💡 Key Takeaways
- 3 to 5 clear bullet points explaining key CS concepts.
""",
        "story": """
## 📖 The Story
Write 3 vivid sentences. Variables are characters, loops are journeys.

## 🗺 Scene by Scene
For EVERY line write:
Line <number>: <exact code>
Story Beat: <one sentence mapping code to story>

## 🎭 The Cast & Moral
- Characters and core lesson.
""",
        "interview": """
## 📌 What It Does
One sentence algorithmic summary.

## ⏱ Complexity
- Time: O(?)
- Space: O(?)

## 🧩 Line-by-Line Walkthrough
Line <number>: <exact code>
Explanation: <algorithmic role>
""",
        "toddler": """
## 🧸 Playground Analogy
2 short sentences. Explain like I'm 5 with toys or snacks.

## 🧩 Step-by-Step Blocks
Line <number>: <exact code>
Simple Idea: <one sentence like talking to a 5 year old>
""",
    }

    # ── Follow-up quick actions ───────────────────────────────────────────────
    FOLLOWUP_ACTIONS = {
        "simpler":   "Re-explain this code in the simplest possible way. Use a 5-year-old level analogy. Short sentences only.",
        "eli5":      "Explain this like I am 5 years old. Use a fun story or toy analogy. Maximum 5 short sentences.",
        "analogy":   "Give one real-world analogy — not tech-related — that maps perfectly to what this code does.",
        "example":   "Show a concrete real-world example of when someone would use this code.",
        "deeper":    "Go deeper on the advanced concepts and trade-offs.",
        "visualize": "Walk through what happens step-by-step in memory when this code runs.",
        "mistakes":  "List the most common mistakes beginners make with this type of code.",
        "compare":   "Compare this approach with 1 or 2 alternatives.",
        "summary":   "Give a 3 to 4 bullet point summary of what this code does.",
    }

    # ── Full Explanation ──────────────────────────────────────────────────────
    def explain(self, code, mode, language, structure, line_focus, comprehension_score, struggles_summary=None):
        mode_key = self._normalize_mode(mode)
        system = self.MODE_PROMPTS.get(mode_key, self.MODE_PROMPTS["academic"])
        prompt = self._build_explain_prompt(code, language, structure, line_focus, comprehension_score, mode_key, struggles_summary)
        text = self._call_gemini(system, prompt)

        parsed = self._parse_ai_response(text)
        return {
            "explanation": parsed.get("explanation", text),
            "line_explanations": parsed.get("line_explanations", []),
            "possible_misconception": parsed.get("possible_misconception", None),
            "concept_teaching": parsed.get("concept_teaching", None),
            "concept_check": parsed.get("concept_check", None),
            "complexity": parsed.get("complexity", {}),
            "mode_used": mode_key,
        }

    # ── Follow-up ─────────────────────────────────────────────────────────────
    def followup(self, code, language, current_explanation, message,
                 action, chat_history, comprehension_score):
        if action and action in self.FOLLOWUP_ACTIONS:
            user_message = self.FOLLOWUP_ACTIONS[action]
        else:
            user_message = message

        system_prompt = """You are LineByLine — an AI programming learning tutor.
STRICT RULES for every reply:
- Use bullet points or numbered lists. Never long paragraphs.
- Keep each point to one clear sentence.
- Maximum 15 words per bullet item.
- End with one short encouraging sentence if the user seemed confused."""

        history_text = ""
        if chat_history:
            history_text = "\n\nPrevious conversation:\n"
            for turn in chat_history[-6:]:
                role = "User" if turn["role"] == "user" else "Tutor"
                history_text += f"{role}: {turn['content']}\n"

        user_prompt = f"""The user is learning about this {language} code:
``` {language}
{code[:800]}{"..." if len(code) > 800 else ""}
```
Previous explanation summary:
{current_explanation[:300]}{"..." if len(current_explanation) > 300 else ""}
{history_text}

Comprehension score: {comprehension_score}/100
User request: {user_message}

Reply using bullet points or a numbered list. No long paragraphs."""

        reply = self._call_gemini(system_prompt, user_prompt)
        suggestion = self._suggest_next_action(action, comprehension_score)
        return {"reply": reply, "suggestion": suggestion}

    # ── Block-by-Block ────────────────────────────────────────────────────────
    def explain_blocks(self, blocks, mode, language):
        results = []
        mode_key = self._normalize_mode(mode)
        system = self.MODE_PROMPTS.get(mode_key, self.MODE_PROMPTS["academic"])

        for block in blocks:
            prompt = f"""Explain this {language} code block in {mode_key} mode.
Block {block['index']}: {block['title']} (lines {block['start_line']} to {block['end_line']})

``` {language}
{block['code']}
```

Return ONLY this JSON:
{{
  "summary": "<one-line heading>",
  "explanation": "<bullet point markdown>",
  "key_concept": "<3 to 5 word concept>"
}}"""

            try:
                text = self._call_gemini(system, prompt)
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

        target = lines[line_num - 1]
        ctx_start = max(0, line_num - 4)
        ctx_end = min(len(lines), line_num + 3)
        context = "\n".join(lines[ctx_start:ctx_end])
        mode_key = self._normalize_mode(mode)
        system = self.MODE_PROMPTS.get(mode_key, self.MODE_PROMPTS["academic"])
        prompt = f"""Explain line {line_num} of this {language} code.
Context:
``` {language}
{context}
```
The line: {target.strip()}

Return ONLY this JSON:
{{"line": {line_num}, "code": "{target.strip()}", "explanation": "<explanation sentence>", "concept": "<3-5 word concept>"}}"""

        text = self._call_gemini(system, prompt)
        try:
            result = self._extract_json(text)
            if isinstance(result, dict):
                clean_exp = re.sub(r'[{}\[\]"\'`]', '', result.get("explanation", "")).strip()
                return {"explanation": clean_exp, "concept": result.get("concept", "")}
            return {"explanation": text, "concept": ""}
        except Exception:
            clean = re.sub(r'[{}\[\]"\'`]', '', text).strip()
            return {"explanation": clean, "concept": ""}

    # ── Concept Teaching (POST /api/teach) ──────────────────────────────────
    def teach_concept(self, code, misconception, concept, mode="academic", language="python"):
        mode_key = self._normalize_mode(mode)
        system = self.MODE_PROMPTS.get(mode_key, self.MODE_PROMPTS["academic"])
        prompt = f"""Teach this programming concept to a student who showed a possible misconception.
Student Code:
```{language}
{code}
```
Detected Possible Misconception: {misconception or 'Conceptual confusion in code logic'}
Concept to Teach: {concept or 'Core Programming Mechanics'}

Explain the concept clearly, provide a simple working code example, connect it to the student's code, and explain a common mistake.

Return ONLY a single valid JSON object matching this schema:
{{
  "concept": "{concept or 'Core Concept'}",
  "explanation": "<clear concept explanation in {mode_key} tone>",
  "simple_example": "<short code example showing correct usage>",
  "connection_to_code": "<how this concept directly relates to their code>",
  "common_mistake": "<what beginners commonly get wrong>"
}}"""

        text = self._call_gemini(system, prompt)
        parsed = self._parse_ai_response(text)
        if isinstance(parsed, dict):
            if "concept_teaching" in parsed and isinstance(parsed["concept_teaching"], dict):
                return parsed["concept_teaching"]
            if "explanation" in parsed or "simple_example" in parsed:
                return {
                    "concept": parsed.get("concept", concept or "Core Concept"),
                    "explanation": parsed.get("explanation", text),
                    "simple_example": parsed.get("simple_example", "items = [10, 20, 30]\nprint(items[0])"),
                    "connection_to_code": parsed.get("connection_to_code", "Relates directly to the structure of your code."),
                    "common_mistake": parsed.get("common_mistake", "Confusing list size with the highest valid index.")
                }
        return {
            "concept": concept or "Programming Concept",
            "explanation": text,
            "simple_example": "# Example code showing correct usage\nitems = [10, 20, 30]\nprint(items[0])",
            "connection_to_code": "Relates directly to the structure of your submitted code.",
            "common_mistake": "Confusing array size with the highest valid index."
        }


    # ── Concept Check Quiz (POST /api/concept-check) ────────────────────────
    def generate_concept_check(self, code, concept, mode="academic", language="python"):
        mode_key = self._normalize_mode(mode)
        system = self.MODE_PROMPTS.get(mode_key, self.MODE_PROMPTS["academic"])
        prompt = f"""Generate a 4-option multiple-choice concept check quiz based on this programming concept and code.
Student Code:
```{language}
{code}
```
Concept: {concept or 'Core Programming Logic'}

Create 1 clear question, 4 distinct options (only 1 correct), the index of the correct answer (0, 1, 2, or 3), and a concise explanation.

Return ONLY a single valid JSON object matching this schema:
{{
  "question": "<conceptual multiple choice question>",
  "options": ["<choice 0>", "<choice 1>", "<choice 2>", "<choice 3>"],
  "correct_index": 1,
  "explanation": "<explanation of why option 1 is correct>"
}}"""

        text = self._call_gemini(system, prompt)
        parsed = self._parse_ai_response(text)
        if isinstance(parsed, dict) and "options" in parsed and len(parsed.get("options", [])) >= 3:
            return parsed
        return {
            "question": f"What is the key rule when working with {concept or 'array indexing'}?",
            "options": ["Indices start at 0", "Indices start at 1", "Arrays expand automatically", "Highest index equals array length"],
            "correct_index": 0,
            "explanation": "In zero-based indexing systems, the first element is at index 0, so valid indices range from 0 to N-1."
        }


    # ── Adaptive Mode Resolution ──────────────────────────────────────────────
    def resolve_adaptive_mode(self, score):
        if score < 45:  return "toddler"
        if score < 75:  return "academic"
        return "interview"

    # ── Phase 8: Dynamic Prerequisite Chain + Next-Step Guidance ─────────────
    # 🔴 NO prerequisite_edges table. Gemini dynamically infers the chain.
    # 🔴 NO misconception_catalog. Learner context is provided inline.
    def generate_prerequisite_chain(
        self,
        target_concept,
        mastery_snapshot=None,
        struggles=None,
        errors=None,
        language="python",
    ):
        """
        DYNAMICALLY (per-request) identify what concepts a learner must master
        BEFORE tackling the `target_concept`. Returns:
          {
            "prerequisite_chain": [  // ordered: foundations FIRST, target LAST
                {"concept": "Variables", "why": "...", "mastery_score": 0.84, "status": "mastered|weak|missing"},
                ...
                {"concept": target_concept, "why": "...", "mastery_score": ..., "status": "..."}
            ],
            "next_steps": [
                {"action": "...", "priority": "high|medium|low", "concept": "...", "estimated_minutes": 5},
                ...
            ],
            "recommended_action": "...one sentence headline the learner should do RIGHT NOW...",
            "guidance_summary": "...short paragraph explaining the learning plan...",
          }

        Best-effort: if Gemini is unavailable, returns None — caller falls
        back to the rule-based heuristic in resources.py.
        """
        if not target_concept or not self.client:
            return None

        mastery_snapshot = mastery_snapshot or []
        struggles = struggles or {}
        errors = errors or {}

        # Build a compact learner context string. Keep it short — Gemini handles
        # the reasoning, we just provide the facts.
        ctx_lines = []
        if mastery_snapshot:
            ctx_lines.append("Learner mastery scores (known concepts, 0.00–1.00):")
            for m in list(mastery_snapshot)[:12]:
                ctx_lines.append(
                    f"  - {m.get('concept_name') or m.get('concept_id')}: "
                    f"{float(m.get('mastery_score') or 0.0):.2f} "
                    f"(attempts={m.get('attempts',0)}, struggles={m.get('struggle_count',0)})"
                )
        if struggles:
            ctx_lines.append("Repeated struggles (concept → count):")
            for c, n in list(struggles.items())[:8]:
                ctx_lines.append(f"  - {c}: {n}x")
        if errors:
            ctx_lines.append("Frequent errors (type → count):")
            for e, n in list(errors.items())[:6]:
                ctx_lines.append(f"  - {e}: {n}x")
        learner_ctx = "\n".join(ctx_lines) or "No prior learner data available (new learner)."

        sys_prompt = (
            "You are an expert CS curriculum designer for a beginner-to-intermediate Python tutor. "
            f"The learner is trying to learn: **{target_concept}** (language: {language}).\n\n"
            "YOUR TASK:\n"
            "1. Dynamically identify the ordered chain of prerequisite concepts the learner\n"
            "   should ideally understand BEFORE (or alongside) tackling this target.\n"
            "   - DO NOT reference any static graph. Use your general CS pedagogy knowledge.\n"
            "   - Keep the chain SHORT (1–4 prerequisites + target at the end = 2–5 items total).\n"
            "   - Every prerequisite must be a real, teachable concept (not vague like 'basics').\n"
            "2. For each item, briefly explain WHY it is a prerequisite (1 sentence, 80 chars max).\n"
            "3. Infer each item's mastery status using the learner-context provided:\n"
            "   - 'mastered' if score >= 0.75  OR  seen >= 4 times with 0 struggles.\n"
            "   - 'weak'     if 0.25 <= score < 0.75  OR  seen 1–3 times with struggles.\n"
            "   - 'missing'  if score < 0.25  OR  concept never seen before.\n"
            "4. Recommend 2–4 concrete, actionable next steps (not URLs — the resources\n"
            "   module already provides URLs from its curated verified library).\n"
            "5. Write a recommended_action headline (1 sentence, learner-facing, 120 chars max).\n"
            "6. Write a short guidance_summary paragraph (2–4 sentences) explaining the plan.\n\n"
            "CRITICAL RULES (NEVER BREAK THESE):\n"
            "- Respond ONLY as valid JSON. No markdown, no extra prose, no code fences.\n"
            "- prerequisite_chain MUST be an ARRAY of objects, each with exactly these keys:\n"
            "    concept: string\n"
            "    why: string (1 short sentence, under 80 chars)\n"
            "    mastery_score: number 0.00–1.00 (infer from context, 0.00 if unknown)\n"
            "    status: one of ['mastered','weak','missing']\n"
            "  The CHAIN IS ORDERED: earliest foundations first, then prerequisites build\n"
            "  upward, and the FINAL item MUST BE the target concept itself.\n"
            "- next_steps MUST be an ARRAY of 2–4 objects, each with:\n"
            "    action: string  (learner-facing imperative, e.g. 'Watch the 5-min guide to Lists')\n"
            "    priority: one of ['high','medium','low']\n"
            "    concept: string  (link to the prerequisite_chain concept name, exact match when possible)\n"
            "    estimated_minutes: integer 1..60\n"
            "- recommended_action: string (1 sentence)\n"
            "- guidance_summary: string (2–4 sentences, paragraph form, learner-facing warm tone)"
        )

        user_prompt = (
            f"## Target concept to learn\n{target_concept}\n\n"
            f"## Programming language\n{language}\n\n"
            f"## Learner context\n{learner_ctx}\n\n"
            "## Output\nReturn a single JSON object matching the required schema."
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=sys_prompt + "\n\n---\n\nUSER:\n" + user_prompt,
                config={"temperature": 0.1, "response_mime_type": "application/json"},
            )
            text = getattr(response, "text", None) or ""
            data = self._extract_json(text)
            if not isinstance(data, dict):
                return None

            # --- Validate & coerce prerequisite_chain ---
            raw_chain = data.get("prerequisite_chain")
            if not isinstance(raw_chain, list) or len(raw_chain) == 0:
                return None
            cleaned_chain = []
            STATUS_ALLOWED = {"mastered", "weak", "missing"}
            for item in raw_chain:
                if not isinstance(item, dict):
                    continue
                c = str(item.get("concept") or "").strip()
                if not c:
                    continue
                try:
                    ms = float(item.get("mastery_score") or 0.0)
                except Exception:
                    ms = 0.0
                ms = 0.0 if ms < 0 else (1.0 if ms > 1 else ms)
                st = str(item.get("status") or "missing").lower()
                if st not in STATUS_ALLOWED:
                    st = "missing"
                cleaned_chain.append({
                    "concept": c,
                    "why": str(item.get("why") or "").strip()[:120],
                    "mastery_score": round(ms, 2),
                    "status": st,
                })
            if not cleaned_chain:
                return None
            # Guarantee target concept is last
            if cleaned_chain[-1]["concept"].lower() != str(target_concept).strip().lower():
                cleaned_chain.append({
                    "concept": str(target_concept).strip(),
                    "why": f"Target concept you want to master.",
                    "mastery_score": cleaned_chain[-1]["mastery_score"],
                    "status": cleaned_chain[-1]["status"],
                })
            data["prerequisite_chain"] = cleaned_chain

            # --- Validate & coerce next_steps ---
            raw_steps = data.get("next_steps") or []
            cleaned_steps = []
            PRIO_ALLOWED = {"high", "medium", "low"}
            if isinstance(raw_steps, list):
                for s in raw_steps:
                    if not isinstance(s, dict):
                        continue
                    action = str(s.get("action") or "").strip()
                    if not action:
                        continue
                    prio = str(s.get("priority") or "medium").lower()
                    if prio not in PRIO_ALLOWED:
                        prio = "medium"
                    try:
                        mins = int(s.get("estimated_minutes") or 5)
                    except Exception:
                        mins = 5
                    mins = 1 if mins < 1 else (60 if mins > 60 else mins)
                    cleaned_steps.append({
                        "action": action[:200],
                        "priority": prio,
                        "concept": str(s.get("concept") or "").strip()[:80],
                        "estimated_minutes": mins,
                    })
            if not cleaned_steps:
                cleaned_steps.append({
                    "action": f"Review the verified resources for {target_concept}.",
                    "priority": "high",
                    "concept": str(target_concept),
                    "estimated_minutes": 10,
                })
            data["next_steps"] = cleaned_steps[:4]

            # --- Simple strings ---
            data["recommended_action"] = str(
                data.get("recommended_action")
                or f"First, strengthen your understanding of {cleaned_chain[0]['concept']}, then tackle {target_concept}."
            )[:200]
            data["guidance_summary"] = str(
                data.get("guidance_summary")
                or "Start with the foundational concepts listed below. Work through the verified resources, then return to practice with concept checks."
            )[:1500]

            return data

        except Exception as exc:
            # Persistence-style best-effort: never crash the recs endpoint.
            print(f"[explainer] WARN: generate_prerequisite_chain failed: {exc!r}")
            return None

    def _normalize_mode(self, mode):
        m = (mode or "").lower()
        if m in ("toddler", "eli5"): return "toddler"
        if m in ("story",): return "story"
        if m in ("interview",): return "interview"
        return "academic"

    # ── Prompt Builder ────────────────────────────────────────────────────────
    def _build_explain_prompt(self, code, language, structure, line_focus, score, mode, struggles_summary=None):
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

        fmt = self.STRUCTURE_FORMAT_RULES.get(mode, self.STRUCTURE_FORMAT_RULES["academic"])

        return f"""Analyze and explain this {language} code for a student learner.
Detected: {'; '.join(parts) or 'basic code'} | Learner score: {score}/100

``` {language}
{code}
```

{fmt}

IMPORTANT: You must analyze the student code for possible conceptual misunderstandings.
Always present any detected misconception as a *possible misconception* using cautious phrasing (e.g., "You may be confusing..."). Do NOT state definitive claims like "You have this error".

Return ONLY a single valid JSON object with NO markdown fences wrapping it, matching this schema:
{{
  "explanation": "<structured markdown explanation>",
  "line_explanations": [
    {{"line": 1, "code": "<source code line>", "note": "<what this line does>"}}
  ],
  "possible_misconception": {{
    "title": "<Short Concept Name e.g. Array Boundaries / Off-by-one>",
    "description": "You may be confusing the number of elements with the highest valid index.",
    "concept_name": "Array Indexing"
  }},
  "concept_teaching": {{
    "concept": "Zero-Based Indexing",
    "explanation": "In programming, index positions start at 0. An array of size N has valid indices from 0 to N-1.",
    "simple_example": "arr = [10, 20, 30]\n# arr[0] is 10, arr[2] is 30. arr[3] is an IndexError!",
    "common_mistake": "Using range(1, len(arr) + 1) or checking arr[len(arr)]."
  }},
  "concept_check": {{
    "question": "If an array contains 5 elements, what is the highest valid index?",
    "options": ["5", "4", "0", "1"],
    "correct_index": 1,
    "explanation": "Indices start at 0, so the 5 elements occupy positions 0, 1, 2, 3, and 4. Thus 4 is the highest valid index."
  }},
  "complexity": {{
    "time": "O(N)",
    "space": "O(1)",
    "pattern": "<algorithm pattern if applicable>"
  }}
}}"""

    # ── Gemini API Call Method ─────────────────────────────────────────────────
    def _call_gemini(self, system, user):
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GROQ_API_KEY")
        if not self.client and HAS_GENAI and api_key and api_key != "your_gemini_api_key_here":
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception:
                pass

        if not self.client:
            return self._generate_fallback_response(user)

        try:
            config = types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.2,
                max_output_tokens=3000,
            )
            response = self.client.models.generate_content(
                model=self.model,
                contents=user,
                config=config,
            )
            if hasattr(response, "text") and response.text:
                return response.text
            return str(response)

        except Exception as err:
            import traceback; traceback.print_exc()
            raise ConnectionError(
                f"Gemini API connection error. Check GEMINI_API_KEY. Original: {err}"
            ) from err

    def _generate_fallback_response(self, user_prompt):
        return json.dumps({
            "explanation": "## 🔍 Code Analysis\nThis code executes standard operations cleanly.",
            "line_explanations": [{"line": 1, "code": "code", "note": "Initializes variable"}],
            "possible_misconception": {
                "title": "Array Indexing Boundaries",
                "description": "You may be confusing the total number of elements with the highest valid index.",
                "concept_name": "Zero-Based Indexing"
            },
            "concept_teaching": {
                "concept": "Zero-Based Indexing",
                "explanation": "Indices in programming languages start at 0. An array with 5 elements has valid indices 0 to 4.",
                "simple_example": "items = ['a', 'b']; first = items[0]",
                "common_mistake": "Accessing items[len(items)] causes an out-of-bounds error."
            },
            "concept_check": {
                "question": "What is the highest valid index in an array with 5 elements?",
                "options": ["5", "4", "0", "1"],
                "correct_index": 1,
                "explanation": "Index positions start at 0, so 5 elements use positions 0, 1, 2, 3, and 4."
            },
            "complexity": {"time": "O(1)", "space": "O(1)", "pattern": "Basic Assignment"}
        })

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

    def _extract_json(self, text):
        """
        Robust multi-strategy JSON extractor.
        Never returns a raw JSON-looking string — always produces a dict.
        """
        raw = (text or "").strip()

        # Strategy 1: direct parse (already valid JSON)
        try:
            return json.loads(raw)
        except Exception:
            pass

        # Strategy 2: strip markdown fences (```json ... ```)
        cleaned = re.sub(r"^```(?:json|javascript|python)?\s*\n?", "", raw)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Strategy 3: JSONDecoder.raw_decode — ignores trailing junk text after object
        try:
            decoder = json.JSONDecoder()
            obj, _ = decoder.raw_decode(cleaned)
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass

        # Strategy 4: regex find { ... } block, fix common LLM mistakes
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            candidate = match.group(0)
            # Fix trailing commas before ] or } (Gemini occasionally emits these)
            candidate = re.sub(r",\s*([\]}])", r"\1", candidate)
            try:
                return json.loads(candidate)
            except Exception:
                pass
            # Also try raw_decode on the fixed candidate
            try:
                decoder = json.JSONDecoder()
                obj, _ = decoder.raw_decode(candidate)
                if isinstance(obj, dict):
                    return obj
            except Exception:
                pass

        # Strategy 5: manually regex-extract key textual fields so user never sees raw JSON
        explanation = self._regex_extract_field(cleaned, "explanation")
        line_expl = self._regex_extract_lines(cleaned)
        misconception = self._regex_extract_object(cleaned, "possible_misconception")
        teaching = self._regex_extract_object(cleaned, "concept_teaching")
        check = self._regex_extract_object(cleaned, "concept_check")
        complexity = self._regex_extract_object(cleaned, "complexity")

        fallback_explanation = text if not explanation else explanation
        if len(fallback_explanation) < 40:
            fallback_explanation = text

        return {
            "explanation": fallback_explanation,
            "line_explanations": line_expl,
            "possible_misconception": misconception,
            "concept_teaching": teaching,
            "concept_check": check,
            "complexity": complexity or {},
        }

    def _regex_extract_field(self, text, field):
        """Pull a string field value out of raw JSON-ish text."""
        m = re.search(
            rf'"{re.escape(field)}"\s*:\s*"((?:[^"\\]|\\.)*)"',
            text, re.DOTALL,
        )
        if not m:
            return None
        raw = m.group(1)
        try:
            return bytes(raw, "utf-8").decode("unicode_escape")
        except Exception:
            return raw.replace("\\n", "\n").replace('\\"', '"')

    def _regex_extract_object(self, text, field):
        """Pull a nested JSON object out of raw JSON-ish text."""
        m = re.search(
            rf'"{re.escape(field)}"\s*:\s*(\{{[\s\S]*?\}})',
            text,
        )
        if not m:
            return None
        body = re.sub(r",\s*([\]}])", r"\1", m.group(1))
        try:
            obj = json.loads(body)
            # Unescape any string values inside
            return self._deep_unescape(obj)
        except Exception:
            return None

    def _regex_extract_lines(self, text):
        """Pull line_explanations array out of raw JSON-ish text."""
        m = re.search(r'"line_explanations"\s*:\s*(\[[\s\S]*?\])', text)
        if not m:
            return []
        body = re.sub(r",\s*([\]}])", r"\1", m.group(1))
        try:
            arr = json.loads(body)
            if isinstance(arr, list):
                return [self._deep_unescape(x) for x in arr if isinstance(x, dict)]
        except Exception:
            pass
        return []

    def _deep_unescape(self, obj):
        """Walk dict/list structure and unescape \\n / \\" in string values."""
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                out[k] = self._deep_unescape(v)
            return out
        if isinstance(obj, list):
            return [self._deep_unescape(x) for x in obj]
        if isinstance(obj, str):
            try:
                return obj.encode("utf-8").decode("unicode_escape")
            except Exception:
                return obj.replace("\\n", "\n").replace('\\"', '"')
        return obj

    def _parse_ai_response(self, text):
        result = self._extract_json(text)
        # _extract_json now always returns a dict (never a raw string)
        if isinstance(result, dict):
            # Extra sanitization: unescape all string values at top level
            result = self._deep_unescape(result)
            return result
        return {
            "explanation": text,
            "line_explanations": [],
            "possible_misconception": None,
            "concept_teaching": None,
            "concept_check": None,
            "complexity": {}
        }