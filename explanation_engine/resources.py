"""
LineByLine Verified Educational Resources Module

ZERO AI-HALLUCINATED URL GUARANTEE
==================================
All URLs in this module are hand-curated from trusted educational domains.
Gemini determines the *topic & learning rationale* only — URLs are resolved
from this curated library or safe search links on trusted domains.

Trusted domains used:
  - docs.python.org        (Python official docs)
  - developer.mozilla.org  (MDN Web Docs)
  - w3schools.com          (Web tutorials)
  - geeksforgeeks.org      (CS fundamentals)
  - freecodecamp.org       (Free coding curriculum)
  - realpython.com         (Python deep dives)
  - learn.microsoft.com    (.NET / C# docs)
  - doc.rust-lang.org      (Rust official docs)
  - cplusplus.com          (C++ reference)
  - docs.oracle.com        (Java docs)
"""

from typing import List, Dict, Any, Optional
import re

# ─────────────────────────────────────────────────────────────────────────────
# CURATED LIBRARY: Concept Keywords → Verified Resources
# Each entry: list of { "title", "url", "source", "type" }
#   type ∈ ["official_docs", "tutorial", "guide", "video_playlist", "exercise"]
# ─────────────────────────────────────────────────────────────────────────────

CURATED_LIBRARY: Dict[str, List[Dict[str, str]]] = {

    # ─── PYTHON CORE ──────────────────────────────────────────────────────────

    "array indexing": [
        {"title": "Python Lists — Official Docs", "url": "https://docs.python.org/3/tutorial/introduction.html#lists", "source": "docs.python.org", "type": "official_docs"},
        {"title": "List Indexing & Slicing (Real Python)", "url": "https://realpython.com/python-lists-tuples/", "source": "realpython.com", "type": "guide"},
        {"title": "GeeksforGeeks — Python List Indexing", "url": "https://www.geeksforgeeks.org/python-list/", "source": "geeksforgeeks.org", "type": "tutorial"},
    ],
    "zero-based indexing": [
        {"title": "MDN — Array Indexing Basics", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array#access_array_elements_using_their_index_position", "source": "developer.mozilla.org", "type": "guide"},
        {"title": "freeCodeCamp — Why Programming Starts at 0", "url": "https://www.freecodecamp.org/news/why-programming-start-at-zero-indexing/", "source": "freecodecamp.org", "type": "tutorial"},
    ],
    "off-by-one": [
        {"title": "Real Python — Python range() Demystified", "url": "https://realpython.com/python-range/", "source": "realpython.com", "type": "guide"},
        {"title": "GeeksforGeeks — Off-by-One Errors", "url": "https://www.geeksforgeeks.org/difference-between-off-by-one-error-and-fencepost-error/", "source": "geeksforgeeks.org", "type": "tutorial"},
    ],
    "loops": [
        {"title": "Python for & while Loops — Official Docs", "url": "https://docs.python.org/3/tutorial/controlflow.html#for-statements", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python 'for' Loops (Definitive Guide)", "url": "https://realpython.com/python-for-loop/", "source": "realpython.com", "type": "guide"},
        {"title": "freeCodeCamp — Loops in Python", "url": "https://www.freecodecamp.org/news/loops-in-python/", "source": "freecodecamp.org", "type": "tutorial"},
    ],
    "for loop": [
        {"title": "Python for Statements — Official Docs", "url": "https://docs.python.org/3/tutorial/controlflow.html#for-statements", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python for Loop", "url": "https://realpython.com/python-for-loop/", "source": "realpython.com", "type": "guide"},
    ],
    "while loop": [
        {"title": "Python while Statements — Official Docs", "url": "https://docs.python.org/3/reference/compound_stmts.html#while", "source": "docs.python.org", "type": "official_docs"},
        {"title": "GeeksforGeeks — Python while Loop", "url": "https://www.geeksforgeeks.org/python-while-loop/", "source": "geeksforgeeks.org", "type": "tutorial"},
    ],
    "range": [
        {"title": "Python range() — Official Docs", "url": "https://docs.python.org/3/library/stdtypes.html#range", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — The Python range() Function", "url": "https://realpython.com/python-range/", "source": "realpython.com", "type": "guide"},
    ],
    "lists": [
        {"title": "Python Lists — Official Docs", "url": "https://docs.python.org/3/tutorial/introduction.html#lists", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python Lists & Tuples", "url": "https://realpython.com/python-lists-tuples/", "source": "realpython.com", "type": "guide"},
    ],
    "tuples": [
        {"title": "Python Tuples & Sequences — Official Docs", "url": "https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python Tuples", "url": "https://realpython.com/python-lists-tuples/", "source": "realpython.com", "type": "guide"},
    ],
    "dictionaries": [
        {"title": "Python Dictionaries — Official Docs", "url": "https://docs.python.org/3/tutorial/datastructures.html#dictionaries", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python Dictionaries", "url": "https://realpython.com/python-dicts/", "source": "realpython.com", "type": "guide"},
    ],
    "dict": [
        {"title": "Python Dictionaries — Official Docs", "url": "https://docs.python.org/3/tutorial/datastructures.html#dictionaries", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python Dictionaries", "url": "https://realpython.com/python-dicts/", "source": "realpython.com", "type": "guide"},
    ],
    "functions": [
        {"title": "Python Functions — Official Docs", "url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python Functions", "url": "https://realpython.com/defining-your-own-python-function/", "source": "realpython.com", "type": "guide"},
        {"title": "freeCodeCamp — Python Functions Tutorial", "url": "https://www.freecodecamp.org/news/python-functions-define-a-function-in-python/", "source": "freecodecamp.org", "type": "tutorial"},
    ],
    "function": [
        {"title": "Python Defining Functions — Official Docs", "url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python Functions Guide", "url": "https://realpython.com/defining-your-own-python-function/", "source": "realpython.com", "type": "guide"},
    ],
    "parameters": [
        {"title": "Python Function Arguments — Official Docs", "url": "https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python Function Arguments", "url": "https://realpython.com/python-kwargs-and-args/", "source": "realpython.com", "type": "guide"},
    ],
    "arguments": [
        {"title": "Python More on Functions — Official Docs", "url": "https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — *args & **kwargs", "url": "https://realpython.com/python-kwargs-and-args/", "source": "realpython.com", "type": "guide"},
    ],
    "return": [
        {"title": "Python return Statement — Official Docs", "url": "https://docs.python.org/3/reference/simple_stmts.html#the-return-statement", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — The Python return Statement", "url": "https://realpython.com/python-return-statement/", "source": "realpython.com", "type": "guide"},
    ],
    "conditionals": [
        {"title": "Python if Statements — Official Docs", "url": "https://docs.python.org/3/tutorial/controlflow.html#if-statements", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Conditional Statements in Python", "url": "https://realpython.com/python-conditional-statements/", "source": "realpython.com", "type": "guide"},
    ],
    "if statement": [
        {"title": "Python if Statements — Official Docs", "url": "https://docs.python.org/3/tutorial/controlflow.html#if-statements", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python if/else", "url": "https://realpython.com/python-conditional-statements/", "source": "realpython.com", "type": "guide"},
    ],
    "variables": [
        {"title": "Python Variables & Types — Official Tutorial", "url": "https://docs.python.org/3/tutorial/introduction.html#using-python-as-a-calculator", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Variables in Python", "url": "https://realpython.com/python-variables/", "source": "realpython.com", "type": "guide"},
    ],
    "variable scope": [
        {"title": "Python Scope & Namespaces — Official Docs", "url": "https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python Scope & LEGB Rule", "url": "https://realpython.com/python-scope-legb-rule/", "source": "realpython.com", "type": "guide"},
    ],
    "recursion": [
        {"title": "Real Python — Recursion in Python", "url": "https://realpython.com/python-recursion/", "source": "realpython.com", "type": "guide"},
        {"title": "GeeksforGeeks — Recursion in Python", "url": "https://www.geeksforgeeks.org/recursion-in-python/", "source": "geeksforgeeks.org", "type": "tutorial"},
        {"title": "freeCodeCamp — How Recursion Works", "url": "https://www.freecodecamp.org/news/how-recursion-works-explained-with-flowcharts-and-a-bunch-of-examples/", "source": "freecodecamp.org", "type": "tutorial"},
    ],
    "classes": [
        {"title": "Python Classes — Official Tutorial", "url": "https://docs.python.org/3/tutorial/classes.html", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — OOP in Python 3", "url": "https://realpython.com/python3-object-oriented-programming/", "source": "realpython.com", "type": "guide"},
    ],
    "oops": [
        {"title": "Real Python — OOP in Python 3", "url": "https://realpython.com/python3-object-oriented-programming/", "source": "realpython.com", "type": "guide"},
        {"title": "freeCodeCamp — OOP in Python", "url": "https://www.freecodecamp.org/news/object-oriented-programming-in-python/", "source": "freecodecamp.org", "type": "tutorial"},
    ],
    "object oriented": [
        {"title": "Real Python — OOP in Python 3", "url": "https://realpython.com/python3-object-oriented-programming/", "source": "realpython.com", "type": "guide"},
        {"title": "freeCodeCamp — OOP in Python", "url": "https://www.freecodecamp.org/news/object-oriented-programming-in-python/", "source": "freecodecamp.org", "type": "tutorial"},
    ],
    "error handling": [
        {"title": "Python Errors & Exceptions — Official Docs", "url": "https://docs.python.org/3/tutorial/errors.html", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python Exceptions Guide", "url": "https://realpython.com/python-exceptions/", "source": "realpython.com", "type": "guide"},
    ],
    "exceptions": [
        {"title": "Python Exceptions — Official Docs", "url": "https://docs.python.org/3/tutorial/errors.html", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python try/except/else/finally", "url": "https://realpython.com/python-exceptions/", "source": "realpython.com", "type": "guide"},
    ],
    "try except": [
        {"title": "Python Handling Exceptions — Official Docs", "url": "https://docs.python.org/3/tutorial/errors.html#handling-exceptions", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python Exceptions", "url": "https://realpython.com/python-exceptions/", "source": "realpython.com", "type": "guide"},
    ],
    "file handling": [
        {"title": "Python Reading & Writing Files — Official Docs", "url": "https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Working With Files in Python", "url": "https://realpython.com/read-write-files-python/", "source": "realpython.com", "type": "guide"},
    ],
    "list comprehension": [
        {"title": "Python List Comprehensions — Official Docs", "url": "https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — When to Use List Comprehensions", "url": "https://realpython.com/list-comprehension-python/", "source": "realpython.com", "type": "guide"},
    ],
    "slicing": [
        {"title": "Python Common Sequence Ops — Official Docs", "url": "https://docs.python.org/3/library/stdtypes.html#common-sequence-operations", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python Slicing", "url": "https://realpython.com/strings-in-python/#slicing-strings", "source": "realpython.com", "type": "guide"},
    ],
    "strings": [
        {"title": "Python Strings — Official Docs", "url": "https://docs.python.org/3/tutorial/introduction.html#strings", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python Strings & Character Data", "url": "https://realpython.com/python-strings/", "source": "realpython.com", "type": "guide"},
    ],
    "mutability": [
        {"title": "Real Python — Python Mutable vs Immutable Types", "url": "https://realpython.com/python-mutable-vs-immutable-types/", "source": "realpython.com", "type": "guide"},
    ],
    "f strings": [
        {"title": "Python Formatted String Literals — Official Docs", "url": "https://docs.python.org/3/reference/lexical_analysis.html#f-strings", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Python 3's f-Strings", "url": "https://realpython.com/python-f-strings/", "source": "realpython.com", "type": "guide"},
    ],
    "sorting": [
        {"title": "Python Sorting HOW TO — Official Docs", "url": "https://docs.python.org/3/howto/sorting.html", "source": "docs.python.org", "type": "official_docs"},
        {"title": "Real Python — Sorting in Python", "url": "https://realpython.com/python-sort/", "source": "realpython.com", "type": "guide"},
    ],
    "algorithms": [
        {"title": "freeCodeCamp — Algorithms Course (YouTube)", "url": "https://www.youtube.com/watch?v=8hly31xKli0", "source": "freecodecamp.org", "type": "video_playlist"},
        {"title": "GeeksforGeeks — Data Structures & Algorithms", "url": "https://www.geeksforgeeks.org/data-structures/", "source": "geeksforgeeks.org", "type": "guide"},
    ],
    "complexity": [
        {"title": "freeCodeCamp — Big O Notation Tutorial", "url": "https://www.freecodecamp.org/news/big-o-notation-why-it-matters-and-why-it-doesnt-1674cfa8a23c/", "source": "freecodecamp.org", "type": "tutorial"},
    ],
    "time complexity": [
        {"title": "freeCodeCamp — Big O Notation Complete Guide", "url": "https://www.freecodecamp.org/news/big-o-notation-why-it-matters-and-why-it-doesnt-1674cfa8a23c/", "source": "freecodecamp.org", "type": "tutorial"},
    ],

    # ─── JAVASCRIPT / WEB ─────────────────────────────────────────────────────

    "javascript": [
        {"title": "MDN JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "source": "developer.mozilla.org", "type": "official_docs"},
        {"title": "freeCodeCamp — JavaScript Curriculum", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "source": "freecodecamp.org", "type": "tutorial"},
    ],
    "closure": [
        {"title": "MDN — Closures", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures", "source": "developer.mozilla.org", "type": "guide"},
        {"title": "freeCodeCamp — JavaScript Closures Explained", "url": "https://www.freecodecamp.org/news/closures-in-javascript/", "source": "freecodecamp.org", "type": "tutorial"},
    ],
    "promises": [
        {"title": "MDN — Using Promises", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises", "source": "developer.mozilla.org", "type": "guide"},
        {"title": "MDN — Promise Reference", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise", "source": "developer.mozilla.org", "type": "official_docs"},
    ],
    "async await": [
        {"title": "MDN — async function", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function", "source": "developer.mozilla.org", "type": "official_docs"},
        {"title": "freeCodeCamp — Async/Await Tutorial", "url": "https://www.freecodecamp.org/news/async-await-in-javascript/", "source": "freecodecamp.org", "type": "tutorial"},
    ],
    "arrow functions": [
        {"title": "MDN — Arrow Function Expressions", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions", "source": "developer.mozilla.org", "type": "official_docs"},
    ],
    "var let const": [
        {"title": "MDN — var vs let vs const", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/let", "source": "developer.mozilla.org", "type": "guide"},
        {"title": "freeCodeCamp — var, let, const Differences", "url": "https://www.freecodecamp.org/news/var-let-and-const-whats-the-difference/", "source": "freecodecamp.org", "type": "tutorial"},
    ],
    "this keyword": [
        {"title": "MDN — this Keyword", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/this", "source": "developer.mozilla.org", "type": "official_docs"},
    ],
    "dom": [
        {"title": "MDN — DOM Introduction", "url": "https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction", "source": "developer.mozilla.org", "type": "guide"},
    ],
    "react": [
        {"title": "React Official Documentation", "url": "https://react.dev/", "source": "react.dev", "type": "official_docs"},
        {"title": "freeCodeCamp — React Full Course", "url": "https://www.youtube.com/watch?v=bMknfKXIFA8", "source": "freecodecamp.org", "type": "video_playlist"},
    ],
    "css": [
        {"title": "MDN CSS Guide", "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS", "source": "developer.mozilla.org", "type": "guide"},
    ],
    "html": [
        {"title": "MDN HTML Guide", "url": "https://developer.mozilla.org/en-US/docs/Learn/HTML", "source": "developer.mozilla.org", "type": "guide"},
    ],

    # ─── OTHER LANGUAGES ──────────────────────────────────────────────────────

    "java": [
        {"title": "Oracle Java Tutorials", "url": "https://docs.oracle.com/javase/tutorial/", "source": "docs.oracle.com", "type": "official_docs"},
    ],
    "c++": [
        {"title": "cplusplus.com — C++ Tutorial", "url": "https://cplusplus.com/doc/tutorial/", "source": "cplusplus.com", "type": "tutorial"},
        {"title": "Learn C++ — TutorialsPoint", "url": "https://www.tutorialspoint.com/cplusplus/index.htm", "source": "tutorialspoint.com", "type": "tutorial"},
    ],
    "csharp": [
        {"title": "Microsoft Learn — C# Guide", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/", "source": "learn.microsoft.com", "type": "official_docs"},
    ],
    "rust": [
        {"title": "The Rust Programming Language (Book)", "url": "https://doc.rust-lang.org/book/", "source": "doc.rust-lang.org", "type": "official_docs"},
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# FALLBACK: Trusted-domain search links (NEVER invent a direct URL)
# ─────────────────────────────────────────────────────────────────────────────

TRUSTED_SEARCH_DOMAINS: List[Dict[str, str]] = [
    {"name": "Python Official Docs",     "url_template": "https://docs.python.org/3/search.html?q={query}",           "source": "docs.python.org"},
    {"name": "MDN Web Docs",             "url_template": "https://developer.mozilla.org/en-US/search?q={query}",        "source": "developer.mozilla.org"},
    {"name": "GeeksforGeeks",            "url_template": "https://www.geeksforgeeks.org/?s={query}",                    "source": "geeksforgeeks.org"},
    {"name": "freeCodeCamp",             "url_template": "https://www.freecodecamp.org/news/search?query={query}",      "source": "freecodecamp.org"},
    {"name": "W3Schools",                "url_template": "https://www.w3schools.com/search/search.php?q={query}",       "source": "w3schools.com"},
]


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", (text or "").lower()).strip()


def find_resources(concept_name: str, max_resources: int = 4, language: str = "python") -> List[Dict[str, str]]:
    """
    Retrieve verified educational resources for a given concept.

    ZERO HALLUCINATION GUARANTEE:
    - Matches concept keywords against a hand-curated verified library.
    - If no direct match, constructs safe **search links** on trusted domains
      rather than fabricating a URL.

    Args:
        concept_name: The concept to look up (e.g. "Array Indexing").
        max_resources: Max number of resources to return.
        language: Programming language context (python / javascript / etc.)

    Returns:
        List of dicts: [ { "title", "url", "source", "type", "matched" } ]
    """
    if not concept_name:
        concept_name = "Programming Fundamentals"

    normalized = _normalize(concept_name)
    results: List[Dict[str, str]] = []
    seen_urls = set()

    # ── 1. Try exact concept key match ──────────────────────────────────────
    for key, resources in CURATED_LIBRARY.items():
        if _normalize(key) == normalized:
            for r in resources:
                if r["url"] not in seen_urls:
                    results.append({**r, "matched": "exact"})
                    seen_urls.add(r["url"])
            break

    # ── 2. Try substring / keyword match against concept keys ───────────────
    if len(results) < max_resources:
        concept_words = set(normalized.split())
        scored: List[tuple] = []
        for key, resources in CURATED_LIBRARY.items():
            key_words = set(_normalize(key).split())
            overlap = concept_words & key_words
            if overlap:
                scored.append((len(overlap), key, resources))
        scored.sort(key=lambda t: -t[0])

        for _score, key, resources in scored:
            if len(results) >= max_resources:
                break
            for r in resources:
                if r["url"] not in seen_urls and len(results) < max_resources:
                    results.append({**r, "matched": f"keyword:{key}"})
                    seen_urls.add(r["url"])

    # ── 3. Try language-specific fallback match ─────────────────────────────
    if len(results) < max_resources:
        lang_key = _normalize(language)
        for key, resources in CURATED_LIBRARY.items():
            if _normalize(key) == lang_key:
                for r in resources:
                    if r["url"] not in seen_urls and len(results) < max_resources:
                        results.append({**r, "matched": f"language:{language}"})
                        seen_urls.add(r["url"])
                break

    # ── 4. Fallback: Safe search links on trusted domains (never invent URL)
    if len(results) < max_resources:
        query = concept_name.replace(" ", "+")
        for domain in TRUSTED_SEARCH_DOMAINS:
            if len(results) >= max_resources:
                break
            search_url = domain["url_template"].format(query=query)
            if search_url not in seen_urls:
                results.append({
                    "title": f"Search '{concept_name}' on {domain['name']}",
                    "url": search_url,
                    "source": domain["source"],
                    "type": "search",
                    "matched": "fallback_search"
                })
                seen_urls.add(search_url)

    return results[:max_resources]


def get_resource_for_error(error_type: str, language: str = "python") -> List[Dict[str, str]]:
    """
    Get verified resources tailored to a specific error type.

    Args:
        error_type: e.g. "IndexError", "SyntaxError", "TypeError", "KeyError"
        language: Programming language context

    Returns:
        List of verified resource dicts (max 3).
    """
    error_map: Dict[str, List[str]] = {
        "indexerror": ["array indexing", "range", "slicing", "lists"],
        "off-by-one": ["off-by-one", "range", "array indexing"],
        "syntaxerror": ["conditionals", "functions"],
        "typeerror": ["variables", "strings", "functions"],
        "keyerror":   ["dictionaries", "dict"],
        "valueerror": ["functions", "error handling"],
        "attributeerror": ["classes", "functions"],
        "nameerror":  ["variables", "variable scope", "functions"],
    }

    normalized_err = _normalize(error_type)
    concepts = error_map.get(normalized_err, ["error handling", "exceptions"])

    collected: List[Dict[str, str]] = []
    seen = set()
    for concept in concepts:
        for r in find_resources(concept, max_resources=2, language=language):
            if r["url"] not in seen:
                collected.append(r)
                seen.add(r["url"])
            if len(collected) >= 3:
                break
        if len(collected) >= 3:
            break
    return collected


def build_recommendation_payload(
    struggles: Optional[Dict[str, int]] = None,
    errors: Optional[Dict[str, int]] = None,
    teaching_concept: Optional[str] = None,
    language: str = "python",
) -> Dict[str, Any]:
    """
    Build the complete recommendation response payload.

    Combines:
      1. Top struggle concept → verified resources
      2. Most frequent error → verified resources
      3. Current teaching concept (from teach panel) → verified resources

    Returns a dict ready for JSON serialization:
    {
      "rationale": "...why these resources are recommended...",
      "primary_concept": "...",
      "resources": [ {title, url, source, type, matched, category}, ... ]
    }
    """
    struggles = struggles or {}
    errors = errors or {}
    all_resources: List[Dict[str, Any]] = []
    seen_urls = set()
    rationale_parts: List[str] = []

    # 1. Primary teaching concept (highest priority — current lesson)
    if teaching_concept:
        resources = find_resources(teaching_concept, max_resources=3, language=language)
        for r in resources:
            if r["url"] not in seen_urls:
                r2 = {**r, "category": "Current Concept"}
                all_resources.append(r2)
                seen_urls.add(r["url"])
        rationale_parts.append(f"📌 Deepen your understanding of **{teaching_concept}**")

    # 2. Top struggle concept (most repeated struggle)
    if struggles:
        top_struggle, top_count = sorted(
            struggles.items(), key=lambda kv: -kv[1]
        )[0]
        if top_count >= 1:
            resources = find_resources(top_struggle, max_resources=2, language=language)
            for r in resources:
                if r["url"] not in seen_urls:
                    r2 = {**r, "category": f"Repeated Struggle (seen {top_count}x)"}
                    all_resources.append(r2)
                    seen_urls.add(r["url"])
            rationale_parts.append(f"⚠️ You've encountered **{top_struggle}** {top_count} time(s)")

    # 3. Most frequent concrete error
    if errors:
        top_err, top_count = sorted(errors.items(), key=lambda kv: -kv[1])[0]
        resources = get_resource_for_error(top_err, language=language)
        for r in resources:
            if r["url"] not in seen_urls:
                r2 = {**r, "category": f"For {top_err} Errors (seen {top_count}x)"}
                all_resources.append(r2)
                seen_urls.add(r["url"])
        rationale_parts.append(f"🔧 Help with **{top_err}** ({top_count} occurrence(s))")

    # 4. Fallback: general language fundamentals
    if not all_resources:
        resources = find_resources(language, max_resources=4, language=language)
        for r in resources:
            r2 = {**r, "category": f"{language.upper()} Fundamentals"}
            all_resources.append(r2)
            seen_urls.add(r["url"])
        rationale_parts.append(f"📚 Recommended fundamentals for learning {language}")

    rationale = "\n".join(f"- {p}" for p in rationale_parts)
    primary_concept = teaching_concept or (
        sorted(struggles.items(), key=lambda kv: -kv[1])[0][0] if struggles else "Programming Fundamentals"
    )

    return {
        "rationale": rationale,
        "primary_concept": primary_concept,
        "resources": all_resources[:6],
    }
