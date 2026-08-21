"""
ExplainX Code Parser
Analyzes source code to identify key structural elements
(loops, conditionals, functions, classes, recursion, etc.)
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class CodeStructure:
    language: str
    lines: List[str]
    total_lines: int
    functions: List[Dict]     = field(default_factory=list)
    classes: List[Dict]       = field(default_factory=list)
    loops: List[Dict]         = field(default_factory=list)
    conditionals: List[Dict]  = field(default_factory=list)
    imports: List[str]        = field(default_factory=list)
    variables: List[str]      = field(default_factory=list)
    recursion: bool           = False
    nested_depth: int         = 0
    complexity_hint: str      = "simple"   # simple | moderate | complex

    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "total_lines": self.total_lines,
            "functions": self.functions,
            "classes": self.classes,
            "loops": self.loops,
            "conditionals": self.conditionals,
            "imports": self.imports,
            "variables": self.variables,
            "recursion": self.recursion,
            "nested_depth": self.nested_depth,
            "complexity_hint": self.complexity_hint,
        }


class CodeParser:
    """Language-aware structural parser for source code."""

    # ── Public API ────────────────────────────────────────────────────────────

    def analyze(self, code: str, language: str = "python") -> Dict[str, Any]:
        lines = code.split("\n")
        lang  = language.lower()

        struct = CodeStructure(
            language=lang,
            lines=lines,
            total_lines=len(lines),
        )

        if lang in ("python", "py"):
            self._parse_python(code, lines, struct)
        elif lang in ("javascript", "js", "typescript", "ts"):
            self._parse_js(code, lines, struct)
        elif lang in ("java", "c", "cpp", "c++"):
            self._parse_c_family(code, lines, struct, lang)
        else:
            self._parse_generic(code, lines, struct)

        struct.nested_depth  = self._calc_nesting(lines, lang)
        struct.complexity_hint = self._rate_complexity(struct)

        return struct.to_dict()

    # ── Python Parser ─────────────────────────────────────────────────────────

    def _parse_python(self, code: str, lines: List[str], s: CodeStructure):
        fn_pattern  = re.compile(r"^\s*def\s+(\w+)\s*\(([^)]*)\)")
        cls_pattern = re.compile(r"^\s*class\s+(\w+)")
        for_pattern = re.compile(r"^\s*for\s+\w+")
        whl_pattern = re.compile(r"^\s*while\s+")
        if_pattern  = re.compile(r"^\s*if\s+")
        elif_pat    = re.compile(r"^\s*elif\s+")
        imp_pattern = re.compile(r"^\s*(?:import|from)\s+(\S+)")

        current_fn = None
        for i, line in enumerate(lines, 1):
            m = fn_pattern.match(line)
            if m:
                current_fn = m.group(1)
                s.functions.append({"name": m.group(1), "params": m.group(2), "line": i})
                # Check recursion
                body_start = i
                fn_body = "\n".join(lines[body_start:body_start + 40])
                if re.search(rf"\b{re.escape(m.group(1))}\s*\(", fn_body):
                    s.recursion = True

            m = cls_pattern.match(line)
            if m:
                s.classes.append({"name": m.group(1), "line": i})

            if for_pattern.match(line):
                s.loops.append({"type": "for", "line": i})
            if whl_pattern.match(line):
                s.loops.append({"type": "while", "line": i})
            if if_pattern.match(line) or elif_pat.match(line):
                s.conditionals.append({"line": i})

            m = imp_pattern.match(line)
            if m:
                s.imports.append(m.group(1))

        # Variable assignments (simple heuristic)
        var_pattern = re.compile(r"^\s*([a-z_]\w*)\s*=\s*(?!=)")
        seen = set()
        for line in lines:
            m = var_pattern.match(line)
            if m and m.group(1) not in seen:
                s.variables.append(m.group(1))
                seen.add(m.group(1))

    # ── JavaScript Parser ─────────────────────────────────────────────────────

    def _parse_js(self, code: str, lines: List[str], s: CodeStructure):
        fn_pat  = re.compile(r"(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\(|(\w+)\s*:\s*(?:async\s*)?function)")
        for_pat = re.compile(r"\b(?:for|forEach|map|filter|reduce)\b")
        whl_pat = re.compile(r"\bwhile\s*\(")
        if_pat  = re.compile(r"\bif\s*\(")
        imp_pat = re.compile(r"(?:import|require)\s*\(?['\"]([^'\"]+)")
        cls_pat = re.compile(r"\bclass\s+(\w+)")

        for i, line in enumerate(lines, 1):
            for m in fn_pat.finditer(line):
                name = m.group(1) or m.group(2) or m.group(3)
                if name:
                    s.functions.append({"name": name, "line": i})
            m = cls_pat.search(line)
            if m:
                s.classes.append({"name": m.group(1), "line": i})
            if for_pat.search(line):
                s.loops.append({"type": "for", "line": i})
            if whl_pat.search(line):
                s.loops.append({"type": "while", "line": i})
            if if_pat.search(line):
                s.conditionals.append({"line": i})
            m = imp_pat.search(line)
            if m:
                s.imports.append(m.group(1))

    # ── C/Java/C++ Parser ─────────────────────────────────────────────────────

    def _parse_c_family(self, code: str, lines: List[str], s: CodeStructure, lang: str):
        for i, line in enumerate(lines, 1):
            if re.search(r"\w+\s+\w+\s*\([^)]*\)\s*\{?", line) and "if" not in line and "while" not in line:
                m = re.search(r"(\w+)\s*\([^)]*\)\s*\{?", line)
                if m:
                    s.functions.append({"name": m.group(1), "line": i})
            if re.search(r"\bfor\s*\(", line):
                s.loops.append({"type": "for", "line": i})
            if re.search(r"\bwhile\s*\(", line):
                s.loops.append({"type": "while", "line": i})
            if re.search(r"\bif\s*\(", line):
                s.conditionals.append({"line": i})
            if re.search(r"#include|import", line):
                m = re.search(r"[<\"]([^>\"]+)[>\"]", line)
                if m:
                    s.imports.append(m.group(1))
            if re.search(r"\bclass\s+\w+", line):
                m = re.search(r"class\s+(\w+)", line)
                if m:
                    s.classes.append({"name": m.group(1), "line": i})

    # ── Generic Parser ────────────────────────────────────────────────────────

    def _parse_generic(self, code: str, lines: List[str], s: CodeStructure):
        for i, line in enumerate(lines, 1):
            if re.search(r"\bfor\b", line, re.I):
                s.loops.append({"type": "for", "line": i})
            if re.search(r"\bwhile\b", line, re.I):
                s.loops.append({"type": "while", "line": i})
            if re.search(r"\bif\b", line, re.I):
                s.conditionals.append({"line": i})

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _calc_nesting(self, lines: List[str], lang: str) -> int:
        max_depth, depth = 0, 0
        for line in lines:
            stripped = line.strip()
            if lang in ("python", "py"):
                indent = len(line) - len(line.lstrip())
                depth = indent // 4
            else:
                depth += stripped.count("{") - stripped.count("}")
            max_depth = max(max_depth, depth)
        return max(0, max_depth)

    def _rate_complexity(self, s: CodeStructure) -> str:
        score = len(s.loops) + len(s.conditionals) + len(s.functions) * 2 + s.nested_depth * 3
        if score <= 3:  return "simple"
        if score <= 10: return "moderate"
        return "complex"

    def split_into_blocks(self, code: str, language: str = "python") -> List[Dict]:
        lines         = code.split("\n")
        lang          = language.lower()
        blocks        = []
        current       = []
        current_start = 1
        current_title = "Block 1"
        block_idx     = 1

        def flush(end_line):
            nonlocal block_idx
            snippet = "\n".join(current).strip()
            if snippet:
                blocks.append({
                    "index":      block_idx,
                    "title":      current_title,
                    "start_line": current_start,
                    "end_line":   end_line,
                    "code":       snippet,
                    "line_count": end_line - current_start + 1,
                })
                block_idx += 1

        if lang in ("python", "py"):
            splitter_re = re.compile(r"^(def |class |# ={3,}|# -{3,})")
        elif lang in ("javascript", "js", "typescript", "ts"):
            splitter_re = re.compile(r"^(function |class |const \w+ = |// ={3,})")
        else:
            splitter_re = re.compile(r"^(\s*(public|private|void|int|class|static)\s|function |def |class )")

        for i, line in enumerate(lines, 1):
            stripped    = line.strip()
            is_boundary = bool(splitter_re.match(line)) and i > 1

            if is_boundary and current:
                flush(i - 1)
                current       = [line]
                current_start = i
                if re.match(r"\s*(def |function )", line):
                    m = re.search(r"(def |function )\s*(\w+)", line)
                    current_title = f"Function: {m.group(2)}" if m else f"Block {block_idx}"
                elif re.match(r"\s*class ", line):
                    m = re.search(r"class\s+(\w+)", line)
                    current_title = f"Class: {m.group(1)}" if m else f"Block {block_idx}"
                elif stripped.startswith("#"):
                    current_title = stripped.lstrip("#").strip()[:40] or f"Block {block_idx}"
                else:
                    current_title = f"Block {block_idx}"
            else:
                current.append(line)

            if len(current) >= 40:
                flush(i)
                current       = []
                current_start = i + 1
                current_title = f"Block {block_idx}"

        if current:
            flush(len(lines))

        if not blocks:
            blocks.append({
                "index": 1, "title": "Full Code",
                "start_line": 1, "end_line": len(lines),
                "code": code.strip(), "line_count": len(lines),
            })

        return blocks