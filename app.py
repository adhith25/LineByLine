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

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "explainx-dev-secret-2024")

engine = ExplainXEngine()
parser = CodeParser()


@app.route("/")
def index():
    if "user_id" not in session:
        session["user_id"]             = str(uuid.uuid4())
        session["interaction_history"] = []
        session["comprehension_score"] = 50
        session["last_mode"]           = "beginner"
        session["chat_history"]        = []
    return render_template("index.html")


@app.route("/api/explain", methods=["POST"])
def explain():
    data       = request.get_json()
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

        result = engine.explain(
            code=code, mode=mode, language=language,
            structure=structure, line_focus=line_focus,
            comprehension_score=session.get("comprehension_score", 50),
        )

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
        return jsonify({"error": "Groq connection failed. " + str(e)}), 502
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": "Groq connection failed. " + str(e)}), 502
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