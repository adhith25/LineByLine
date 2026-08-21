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
from urllib.parse import urlparse
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


# ─────────────────────────────────────────────────────────────────────────────
# Phase 8: Rule-based prerequisite chain (fallback when Gemini unavailable)
# NO prerequisite_edges table. This is a small deterministic heuristic map
# covering the 26 seeded canonical concepts. Gemini dynamically enhances
# this with richer rationale + next_steps, but never reads/writes a graph.
# ─────────────────────────────────────────────────────────────────────────────

_RULE_PREREQUISITES: Dict[str, List[str]] = {
    "List Indexing":        ["Variables", "Data Types", "Lists"],
    "Lists":                ["Variables", "Data Types"],
    "Loops":                ["Variables", "Conditionals"],
    "For Loops":            ["Variables", "Conditionals", "Lists"],
    "While Loops":          ["Variables", "Conditionals"],
    "Conditionals":         ["Variables", "Data Types"],
    "If Statements":        ["Variables", "Data Types"],
    "Functions":            ["Variables", "Conditionals"],
    "Parameters":           ["Functions", "Variables"],
    "Return Statements":    ["Functions"],
    "Dictionaries":         ["Variables", "Data Types", "Lists"],
    "Data Types":           ["Variables"],
    "Strings":              ["Variables", "Data Types"],
    "Tuples":               ["Variables", "Data Types", "Lists"],
    "Recursion":            ["Functions", "Conditionals"],
    "Classes":              ["Functions", "Variables", "Data Types"],
    "OOP":                  ["Classes", "Functions", "Variables"],
    "Error Handling":       ["Conditionals", "Functions"],
    "Exceptions":           ["Conditionals", "Functions"],
    "File Handling":        ["Functions", "Strings"],
    "List Comprehensions":  ["Lists", "Loops", "Conditionals"],
    "Slicing":              ["Lists", "Strings", "Data Types"],
    "Variable Scope":       ["Functions", "Variables"],
    "Mutability":           ["Data Types", "Variables", "Lists"],
    "F-Strings":            ["Strings", "Variables", "Data Types"],
    "Sorting":              ["Lists", "Conditionals", "Loops"],
    "Algorithms":           ["Loops", "Conditionals", "Functions", "Lists"],
    "Time Complexity":      ["Algorithms", "Loops"],
    "Big O Notation":       ["Algorithms", "Time Complexity"],
    "Operators & Expressions": ["Variables", "Data Types"],
}


def _rule_mastery_for(concept, mastery_snapshot):
    """Look up a learner's mastery for a concept by name, None if unknown."""
    if not mastery_snapshot:
        return None
    cn = (concept or "").strip().lower()
    for m in mastery_snapshot:
        name = (m.get("concept_name") or m.get("concept_id") or "").strip().lower()
        if name == cn:
            try:
                return float(m.get("mastery_score") or 0.0)
            except Exception:
                return 0.0
    return None


def _status_from_score(score, attempts):
    attempts = int(attempts or 0)
    if score is None:
        return "missing"
    if score >= 0.75:
        return "mastered"
    if score >= 0.25 or attempts >= 1:
        return "weak"
    return "missing"


def build_rule_based_guidance(target_concept, mastery_snapshot=None, struggles=None,
                               errors=None, language="python"):
    """
    Deterministic fallback prerequisite chain + next_steps, used when:
      - Gemini client is unavailable, OR
      - generate_prerequisite_chain() raises/returns None.

    Returns the SAME shape as the Gemini method so caller code is unified.
    """
    target = (target_concept or "Programming Fundamentals").strip()
    mastery_snapshot = mastery_snapshot or []
    struggles = struggles or {}
    errors = errors or {}

    # Build chain: prerequisites first, target last
    chain = []
    seen = set()
    prereq_keys = _RULE_PREREQUISITES.get(target) or _RULE_PREREQUISITES.get(
        _normalize(target)
    ) or []
    # Also do one level of indirect lookup for the prereqs' prereqs (cap: shallow)
    indirect = []
    for p in prereq_keys:
        indirect.extend(_RULE_PREREQUISITES.get(p) or [])
    ordered_prereqs = []
    for p in indirect + prereq_keys:
        if p and p not in seen and p != target:
            ordered_prereqs.append(p)
            seen.add(p)
    # Cap total prerequisites at 4 to keep UI focused
    ordered_prereqs = ordered_prereqs[-4:]

    for concept in ordered_prereqs:
        score = _rule_mastery_for(concept, mastery_snapshot)
        attempts = 0
        for m in mastery_snapshot:
            name = (m.get("concept_name") or m.get("concept_id") or "").strip().lower()
            if name == concept.lower():
                attempts = int(m.get("attempts") or 0)
                break
        why_map = {
            "Variables": "You must store and name values before using them anywhere.",
            "Data Types": "Every value has a type — this shapes what operations work.",
            "Lists": "Collections underpin most iteration and indexing problems.",
            "Conditionals": "Control flow is required before writing any complex logic.",
            "Functions": "Reusable blocks are the building block of modular code.",
            "Loops": "Repeated execution requires solid grasp of iteration mechanics.",
            "Strings": "Most real programs manipulate text before anything else.",
            "Dictionaries": "Key/value lookup is a core container pattern after lists.",
        }
        chain.append({
            "concept": concept,
            "why": why_map.get(concept, f"Foundational idea you should solidify before {target}."),
            "mastery_score": round(score, 2) if score is not None else 0.00,
            "status": _status_from_score(score, attempts),
        })
    # Always append the target concept last
    tgt_score = _rule_mastery_for(target, mastery_snapshot)
    tgt_attempts = 0
    for m in mastery_snapshot:
        name = (m.get("concept_name") or m.get("concept_id") or "").strip().lower()
        if name == target.lower():
            tgt_attempts = int(m.get("attempts") or 0)
            break
    chain.append({
        "concept": target,
        "why": f"The concept you want to master — work on this after the foundations above.",
        "mastery_score": round(tgt_score, 2) if tgt_score is not None else 0.00,
        "status": _status_from_score(tgt_score, tgt_attempts),
    })

    # Next steps: synthesise from the weakest items in the chain
    priority_order = {"missing": 0, "weak": 1, "mastered": 2}
    weakest = sorted(chain, key=lambda c: (priority_order.get(c["status"], 3), c["mastery_score"]))
    next_steps = []
    if weakest and weakest[0]["status"] != "mastered":
        first = weakest[0]
        next_steps.append({
            "action": f"Open the verified resources below for {first['concept']} and spend 5 minutes reading the concept overview.",
            "priority": "high",
            "concept": first["concept"],
            "estimated_minutes": 5,
        })
    if len(weakest) >= 2 and weakest[1]["status"] != "mastered":
        second = weakest[1]
        next_steps.append({
            "action": f"Complete 1–2 small practice exercises on {second['concept']} to build muscle memory.",
            "priority": "medium",
            "concept": second["concept"],
            "estimated_minutes": 10,
        })
    next_steps.append({
        "action": f"Return to {target} and re-take the concept check to confirm progress.",
        "priority": "medium",
        "concept": target,
        "estimated_minutes": 5,
    })

    # Recommended action + summary
    if weakest:
        first_concept = weakest[0]["concept"]
        recommended_action = (
            f"First, shore up {first_concept} using the verified resources below, "
            f"then return to practice {target}."
        )
    else:
        recommended_action = f"Work through the verified resources for {target} and complete the concept check."
    guidance_summary = (
        f"Here's a focused plan to learn {target}. Start with the foundational "
        "items flagged 'missing' or 'weak' — each one links to curated verified "
        "resources from trusted sources. After reviewing the weakest concept, "
        "do a short practice session, then come back to the concept check to "
        "confirm mastery. Go step by step and don't rush — small wins compound!"
    )

    return {
        "prerequisite_chain": chain,
        "next_steps": next_steps[:4],
        "recommended_action": recommended_action,
        "guidance_summary": guidance_summary,
        "source": "rule_based_fallback",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Phase 8 Addendum — URL Sanitizer (ZERO-HALLUCINATION ENFORCEMENT)
#
# Current Phase 5 guarantees URLs never come from Gemini — only CURATED_LIBRARY
# and TRUSTED_SEARCH_DOMAINS produce URLs. However, to ensure future code
# changes or integration mistakes cannot surface untrusted URLs, we add a
# defensive validation+sanitization layer:
#
#   1. Each URL must be http/https scheme.
#   2. Each URL's hostname must be in the explicit TRUSTED_HOSTNAME_ALLOWLIST
#      (derived from CURATED_LIBRARY + TRUSTED_SEARCH_DOMAINS plus known safe
#      official language sites).
#   3. Any placeholder / example / TLD-invalid / IP-host / localhost URL is
#      immediately considered invalid.
#   4. Any invalid resource → discarded and replaced with a find_resources()
#      lookup on the same concept.
#
# NEVER read URLs from Gemini. This layer is a belt-and-braces defense.
# ─────────────────────────────────────────────────────────────────────────────

def _extract_hostnames_from_curated_library() -> List[str]:
    """Scan CURATED_LIBRARY + TRUSTED_SEARCH_DOMAINS for all unique hostnames."""
    hosts: set = set()
    for resources in CURATED_LIBRARY.values():
        for r in resources:
            try:
                h = urlparse(r["url"]).hostname
                if h:
                    hosts.add(h.lower())
            except Exception:
                pass
    for domain in TRUSTED_SEARCH_DOMAINS:
        try:
            tpl = domain["url_template"].format(query="placeholder")
            h = urlparse(tpl).hostname
            if h:
                hosts.add(h.lower())
        except Exception:
            pass
    # Known official/trustworthy sites we explicitly want to allow even if no
    # current curated URL references them.
    hosts |= {
        "react.dev", "reactjs.org", "vitejs.dev", "tailwindcss.com",
        "getbootstrap.com", "vuejs.org", "angular.io",
        "nodejs.org", "npmjs.com", "pypi.org", "crates.io",
        "learn.microsoft.com", "docs.aws.amazon.com", "cloud.google.com",
    }
    return sorted(hosts)


TRUSTED_HOSTNAME_ALLOWLIST: List[str] = _extract_hostnames_from_curated_library()

# Regex to match hostnames that are clearly invalid/placeholder/non-routable.
_BAD_HOST_PATTERNS = [
    re.compile(r"(^|\.)example\.(com|org|net)$", re.I),
    re.compile(r"(^|\.)placeholder\.|placeholder", re.I),
    re.compile(r"(^|\.)tbd\.|to-be-determined|todo|your[-_]?", re.I),
    re.compile(r"(^|\.)test\.(com|org|net)$", re.I),
    re.compile(r"(^|\.)localhost$", re.I),
    re.compile(r"(^|\.)invalid$", re.I),
    re.compile(r"(^|\.)local$", re.I),
    re.compile(r"(^|\.)internal$", re.I),
    re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"),  # raw IPv4
    re.compile(r"^localhost$", re.I),
]


def is_url_safe(url: Optional[str]) -> bool:
    """
    Returns True ONLY when a URL:
      - Is a non-empty string
      - Parses as http: or https: scheme only
      - Has a valid hostname with a real TLD (.com .org etc.)
      - Matches TRUSTED_HOSTNAME_ALLOWLIST
      - Does NOT match any BAD_HOST_PATTERNS
      - Is NOT a placeholder, example, IP, localhost, or obviously-fabricated string
    """
    if not url or not isinstance(url, str):
        return False
    s = url.strip()
    if len(s) < 12:  # "https://a.co" is 12 — shorter is impossible for a real URL
        return False
    try:
        parsed = urlparse(s)
    except Exception:
        return False
    if parsed.scheme.lower() not in ("http", "https"):
        return False
    host = (parsed.hostname or "").lower().strip()
    if not host:
        return False
    # No raw IPs, no placeholders, no example/invalid/test/localhost domains
    for pat in _BAD_HOST_PATTERNS:
        if pat.search(host):
            return False
    # Must have at least one dot, and the TLD part 2 chars or more (real TLDs)
    if "." not in host:
        return False
    tld = host.rsplit(".", 1)[-1]
    if len(tld) < 2 or not tld.isalpha():
        return False
    # Final gate: hostname must be in the curated allowlist.
    # Check both exact match and eTLD+1 match (e.g. docs.python.org → python.org)
    if host in TRUSTED_HOSTNAME_ALLOWLIST:
        return True
    parts = host.split(".")
    if len(parts) >= 2:
        etld1 = ".".join(parts[-2:])
        if etld1 in TRUSTED_HOSTNAME_ALLOWLIST:
            return True
    return False


def sanitize_resource_list(
    resources: List[Dict[str, Any]],
    fallback_concept: Optional[str],
    language: str = "python",
    max_resources: int = 6,
) -> List[Dict[str, Any]]:
    """
    Validate every resource URL. Discard any invalid entries and replace them
    with find_resources() results on `fallback_concept`. Guarantee the
    resulting list only contains URLs for which is_url_safe() is True.

    - Invalid/missing url → drop row.
    - If fewer than min(1, original_length) valid rows remain → generate
      fresh find_resources() list.
    - Never returns more than `max_resources`.
    """
    if not isinstance(resources, list):
        resources = []
    fallback_concept = (fallback_concept or "Programming Fundamentals").strip()

    kept: List[Dict[str, Any]] = []
    seen_urls: set = set()
    invalid_count = 0

    for r in resources:
        if not isinstance(r, dict):
            invalid_count += 1
            continue
        url = r.get("url")
        if not is_url_safe(url):
            invalid_count += 1
            continue
        title = str(r.get("title") or "Untitled resource").strip()[:120] or "Untitled resource"
        source = str(r.get("source") or (urlparse(url).hostname or "unknown")).strip()[:60]
        rtype = str(r.get("type") or "search").strip()
        if rtype not in ("official_docs", "tutorial", "guide", "video_playlist", "exercise", "search"):
            rtype = "search"
        if url in seen_urls:
            continue
        safe_row: Dict[str, Any] = {
            "title": title,
            "url": url,
            "source": source,
            "type": rtype,
        }
        for k in ("matched", "category"):
            if k in r and r[k]:
                safe_row[k] = str(r[k])[:80]
        kept.append(safe_row)
        seen_urls.add(url)
        if len(kept) >= max_resources:
            break

    # If nothing survived the filter OR we tossed some rows, top up with
    # verified find_resources() output (already known safe because it comes
    # from the curated dict — we still re-validate for belt-and-braces).
    need_more = max_resources - len(kept)
    if invalid_count > 0 or need_more > 0:
        fresh = find_resources(fallback_concept, max_resources=max(need_more, 1), language=language)
        for r in fresh:
            if len(kept) >= max_resources:
                break
            if not is_url_safe(r.get("url")):
                continue
            url = r["url"]
            if url in seen_urls:
                continue
            kept.append(r)
            seen_urls.add(url)

    # Final guard: re-run is_url_safe() across the entire list and drop any
    # last stragglers. Should never occur.
    final = [r for r in kept if is_url_safe(r.get("url"))]
    return final[:max_resources]
