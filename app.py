"""
ExplainX – Multi-Perspective Code Explanation Engine
Flask Backend
"""

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, jsonify, session
import os, uuid
from explanation_engine.explainer import ExplainXEngine
from explanation_engine.parser import CodeParser
from explanation_engine.resources import build_recommendation_payload

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "explainx-dev-secret-2024")

engine = ExplainXEngine()
parser = CodeParser()


def _ensure_session_defaults():
    if "user_id" not in session:
        session["user_id"]             = str(uuid.uuid4())
        session["interaction_history"] = []
        session["comprehension_score"] = 50
        session["last_mode"]           = "beginner"
        session["chat_history"]        = []
    if "struggles" not in session:
        session["struggles"] = {}
    if "errors" not in session:
        session["errors"] = {}
    if "concept_checks" not in session:
        session["concept_checks"] = {}
    if "recent_improvements" not in session:
        session["recent_improvements"] = []

def _detect_error_type(code, result):
    combined = (code + " " + str(result)).lower()
    if "indexerror" in combined or "out of range" in combined or "off-by-one" in combined or "index out of bounds" in combined:
        return "IndexError"
    if "syntaxerror" in combined or "invalid syntax" in combined or "unexpected token" in combined:
        return "SyntaxError"
    if "typeerror" in combined or "unsupported operand" in combined:
        return "TypeError"
    if "keyerror" in combined:
        return "KeyError"
    return None

def _build_struggles_summary():
    struggles = session.get("struggles", {})
    errors = session.get("errors", {})
    parts = []
    for concept, count in list(struggles.items())[:3]:
        parts.append(f"encountered {concept} issues {count} times")
    for err, count in list(errors.items())[:3]:
        parts.append(f"encountered {err} {count} times")
    if not parts:
        return None
    return "Learner history: " + ", ".join(parts)


@app.route("/")
def index():
    _ensure_session_defaults()
    return render_template("index.html")


@app.route("/api/explain", methods=["POST"])
def explain():
    _ensure_session_defaults()
    data       = request.get_json() or {}
    code       = data.get("code", "").strip()
    mode       = data.get("mode", "beginner")
    language   = data.get("language", "python")
    line_focus = data.get("line_focus", None)

    if not code:
        return jsonify({"error": "No code provided"}), 400

    try:
        structure = parser.analyze(code, language)

        if mode == "adaptive":
            score = session.get("comprehension_score", 50)
            mode  = engine.resolve_adaptive_mode(score)
            resolved_adaptive = True
        else:
            resolved_adaptive = False

        struggles_summary = _build_struggles_summary()

        result = engine.explain(
            code=code, mode=mode, language=language,
            structure=structure, line_focus=line_focus,
            comprehension_score=session.get("comprehension_score", 50),
            struggles_summary=struggles_summary,
        )

        # Track submission-level struggles
        misconception = result.get("possible_misconception")
        if misconception and isinstance(misconception, dict):
            c_name = misconception.get("concept_name") or misconception.get("title")
            if c_name:
                struggles = dict(session.get("struggles", {}))
                struggles[c_name] = struggles.get(c_name, 0) + 1
                session["struggles"] = struggles

        # Track submission-level concrete errors
        err_type = _detect_error_type(code, result)
        if err_type:
            errors = dict(session.get("errors", {}))
            errors[err_type] = errors.get(err_type, 0) + 1
            session["errors"] = errors

        history = session.get("interaction_history", [])
        history.append({"mode": mode, "code_snippet": code[:120]})
        session["interaction_history"] = history[-10:]
        session["last_mode"]           = mode
        session["chat_history"]        = []
        session["last_code"]           = code
        session["last_language"]       = language
        session["last_mode_used"]      = mode

        return jsonify(result)

    except ConnectionError as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": "Gemini API connection failed. " + str(e)}), 502
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500



@app.route("/api/teach", methods=["POST"])
def teach():
    data          = request.get_json() or {}
    code          = data.get("code", session.get("last_code", "")).strip()
    misconception = data.get("misconception", "")
    concept       = data.get("concept", "")
    mode          = data.get("mode", session.get("last_mode", "academic"))
    language      = data.get("language", session.get("last_language", "python"))

    try:
        result = engine.teach_concept(
            code=code,
            misconception=misconception,
            concept=concept,
            mode=mode,
            language=language
        )
        return jsonify(result)
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/concept-check", methods=["POST"])
def concept_check():
    data     = request.get_json() or {}
    code     = data.get("code", session.get("last_code", "")).strip()
    concept  = data.get("concept", "")
    mode     = data.get("mode", session.get("last_mode", "academic"))
    language = data.get("language", session.get("last_language", "python"))

    try:
        result = engine.generate_concept_check(
            code=code,
            concept=concept,
            mode=mode,
            language=language
        )
        return jsonify(result)
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/quiz-result", methods=["POST"])
def quiz_result():
    _ensure_session_defaults()
    data       = request.get_json() or {}
    concept    = data.get("concept", "General Concept").strip()
    is_correct = bool(data.get("is_correct", False))

    checks = dict(session.get("concept_checks", {}))
    c_stat = checks.get(concept, {"attempts": 0, "correct": 0, "incorrect": 0})
    c_stat["attempts"] += 1
    if is_correct:
        c_stat["correct"] += 1
    else:
        c_stat["incorrect"] += 1
    checks[concept] = c_stat
    session["concept_checks"] = checks

    # Record recent improvement if correct answer achieved
    if is_correct:
        improvements = list(session.get("recent_improvements", []))
        improvements.append({
            "concept": concept,
            "status": "Passed Concept Check",
            "icon": "✓"
        })
        session["recent_improvements"] = improvements[-5:]

    return jsonify({"status": "ok", "stats": c_stat})


@app.route("/api/progress", methods=["GET"])
def get_progress():
    _ensure_session_defaults()
    return jsonify({
        "struggles": session.get("struggles", {}),
        "errors": session.get("errors", {}),
        "concept_checks": session.get("concept_checks", {}),
        "recent_improvements": session.get("recent_improvements", [])
    })


@app.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    """
    Phase 5 — Verified Learning Recommendations.

    ZERO AI-HALLUCINATED URL GUARANTEE:
    - All URLs come from a hand-curated library in explanation_engine/resources.py
    - Gemini (or the explainer) only determines the *topic & rationale* via session.
    - URLs are resolved from trusted domains (docs.python.org, MDN, GeeksforGeeks,
      freeCodeCamp, etc.) — never fabricated.
    - As a last resort, safe search links on trusted domains are returned.

    Uses session data (struggles, errors, last teaching concept) + language
    from last submission to assemble a personalised recommendation payload.
    """
    _ensure_session_defaults()

    teaching_concept = None
    last_concept_checks = session.get("concept_checks", {}) or {}
    if last_concept_checks:
        sorted_concepts = sorted(
            last_concept_checks.items(),
            key=lambda kv: -(kv[1].get("incorrect", 0) * 2 + kv[1].get("attempts", 0))
        )
        teaching_concept = sorted_concepts[0][0]

    payload = build_recommendation_payload(
        struggles=session.get("struggles", {}),
        errors=session.get("errors", {}),
        teaching_concept=teaching_concept,
        language=session.get("last_language", "python"),
    )

    return jsonify(payload)





@app.route("/api/followup", methods=["POST"])
def followup():
    """Handle follow-up questions and re-explanation requests."""
    data                = request.get_json()
    message             = data.get("message", "").strip()
    action              = data.get("action", None)
    code                = data.get("code", session.get("last_code", ""))
    language            = data.get("language", session.get("last_language", "python"))
    current_explanation = data.get("current_explanation", "")

    if not message and not action:
        return jsonify({"error": "No message provided"}), 400

    try:
        chat_history = session.get("chat_history", [])

        result = engine.followup(
            code=code,
            language=language,
            current_explanation=current_explanation,
            message=message,
            action=action,
            chat_history=chat_history,
            comprehension_score=session.get("comprehension_score", 50),
        )

        chat_history.append({"role": "user",      "content": message or action})
        chat_history.append({"role": "assistant",  "content": result["reply"]})
        session["chat_history"] = chat_history[-20:]

        # Lower score slightly when user signals confusion
        if action in ("simpler", "analogy", "eli5"):
            session["comprehension_score"] = max(0, session.get("comprehension_score", 50) - 5)

        return jsonify(result)

    except ConnectionError as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": "Gemini API connection failed. " + str(e)}), 502
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/explain-blocks", methods=["POST"])
def explain_blocks():
    data     = request.get_json()
    code     = data.get("code", "").strip()
    mode     = data.get("mode", "beginner")
    language = data.get("language", "python")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    try:
        if mode == "adaptive":
            score = session.get("comprehension_score", 50)
            mode  = engine.resolve_adaptive_mode(score)

        blocks  = parser.split_into_blocks(code, language)
        results = engine.explain_blocks(blocks, mode, language)
        return jsonify(results)

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/feedback", methods=["POST"])
def feedback():
    data       = request.get_json()
    correct    = data.get("correct", False)
    difficulty = data.get("difficulty", "medium")

    score     = session.get("comprehension_score", 50)
    delta_map = {"easy": 3, "medium": 7, "hard": 12}
    delta     = delta_map.get(difficulty, 7)
    score     = min(100, score + delta) if correct else max(0, score - delta)

    session["comprehension_score"] = score
    return jsonify({"score": score})


@app.route("/api/line-explain", methods=["POST"])
def line_explain():
    data     = request.get_json()
    code     = data.get("code", "")
    line_num = data.get("line", 1)
    mode     = data.get("mode", session.get("last_mode", "beginner"))
    language = data.get("language", "python")
    result   = engine.explain_line(code=code, line_num=line_num, mode=mode, language=language)
    return jsonify(result)


@app.route("/api/session", methods=["GET"])
def get_session():
    return jsonify({"score": session.get("comprehension_score", 50)})


@app.route("/api/reset", methods=["POST"])
def reset_session():
    session["comprehension_score"] = 50
    session["interaction_history"] = []
    session["last_mode"]           = "beginner"
    session["chat_history"]        = []
    return jsonify({"status": "ok"})


def _score_message(score):
    if score >= 80: return "🚀 Excellent grasp! Pushing to advanced explanations."
    if score >= 60: return "👍 Good progress! Balancing detail and clarity."
    if score >= 40: return "📖 Building foundations. Keeping explanations clear."
    return "🌱 Starting fresh. Using simple, friendly language."


if __name__ == "__main__":
    app.run(debug=True, port=5000)