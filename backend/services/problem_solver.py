"""
Tribal AI specialist solver for mathematics and programming.

Additive module: does not alter existing frontend, fonts, CSS, message renderer,
translation service, or existing chat service.

Call prepare_problem_request(question) from the backend before invoking the
existing LLM. For simple arithmetic, it can return a deterministic answer;
otherwise, it returns a specialist system prompt to include in the LLM request.

This module does not execute generated code. It never uses eval().
"""
from __future__ import annotations

import ast
import operator
import re
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class Route:
    kind: str
    confidence: float
    reason: str


OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def classify_problem(question: str) -> Route:
    q = (question or "").strip().lower()
    if not q:
        return Route("general", 0.0, "empty question")

    coding = (
        "three sum", "two sum", "leetcode", "write code", "code in ",
        "program in ", "java", "python", "c++", "javascript", "typescript",
        "sql", "debug", "stack trace", "compile error", "runtime error",
        "algorithm", "time complexity", "space complexity", "implement ",
        "function ", "class ", "linked list", "binary search", "recursion",
    )
    math = (
        "calculate", "solve", "evaluate", "simplify", "equation",
        "differentiate", "integrate", "derivative", "integral", "probability",
        "percentage", "percent", "square root", "quadratic", "arithmetic",
        "multiply", "divide", "plus", "minus", "sum of",
    )
    if any(term in q for term in coding):
        return Route("coding", 0.95, "programming intent")
    if any(term in q for term in math) or re.search(r"\d\s*[\+\-*/%]\s*\d", q):
        return Route("math", 0.90, "mathematics intent")
    return Route("general", 0.60, "general intent")


def _eval_numeric_ast(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval_numeric_ast(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        left, right = _eval_numeric_ast(node.left), _eval_numeric_ast(node.right)
        if isinstance(node.op, ast.Pow) and (abs(right) > 100 or abs(left) > 10**6):
            raise ValueError("Expression outside supported range")
        result = OPS[type(node.op)](left, right)
        if isinstance(result, complex):
            raise ValueError("Complex results are unsupported")
        if isinstance(result, float) and (result != result or abs(result) == float("inf")):
            raise ValueError("Non-finite result")
        return result
    raise ValueError("Unsupported arithmetic expression")


def calculate_simple_arithmetic(question: str) -> Optional[dict[str, Any]]:
    """Calculate a simple numeric expression safely, or return None."""
    text = (question or "").strip()
    if not text or len(text) > 180:
        return None

    # Accept a bare expression, or a common phrase such as "What is 125 * 48?"
    candidate = re.sub(
        r"^(?:what is|calculate|compute|evaluate|solve)\s+",
        "", text, flags=re.IGNORECASE
    ).strip().rstrip("?.! ")
    if not re.fullmatch(r"[\d\s.+\-*/()%]+", candidate):
        # Extract a conservative expression only if the surrounding sentence
        # contains exactly one likely arithmetic span.
        spans = re.findall(r"(?<![\w.])[\d(][\d\s.+\-*/()%]*[\d)]", text)
        spans = [s.strip() for s in spans if re.search(r"[+*/%]|(?<!^)-", s)]
        if not spans:
            return None
        candidate = max(spans, key=len)
        if not re.fullmatch(r"[\d\s.+\-*/()%]+", candidate):
            return None
    if not re.search(r"[+*/%]|(?<!^)-", candidate):
        return None

    try:
        value = _eval_numeric_ast(ast.parse(candidate, mode="eval").body)
    except (SyntaxError, ValueError, ZeroDivisionError, OverflowError):
        return None

    answer = int(value) if isinstance(value, float) and value.is_integer() else value
    return {
        "expression": candidate,
        "answer": answer,
        "formatted_answer": f"{candidate} = {answer}",
        "verified": True,
        "method": "safe arithmetic evaluator",
    }


def specialist_system_prompt(kind: str) -> str:
    common = """
You are Tribal AI, an accurate, clear assistant.
Answer the actual question in the requested language. Do not invent tool results,
citations, compilation results, or test results.
Use valid Markdown. Keep mathematical equations intact and never turn equation
fragments into separate bullet points. Do not output HTML fragments or the literal
string [object Object]. Never put source code in inline code.
""".strip()

    if kind == "coding":
        return common + """

CODING DEFAULTS
- Give a complete solution by default when asked to solve or implement a coding problem.
- Put the entire source in one fenced code block labelled with its language.
- Source code must have real line breaks and conventional indentation; never flatten it.
- Include imports and a runnable main/example when appropriate.
- Explain the algorithm, relevant edge cases, and correctness idea.
- For algorithm questions, state time and auxiliary-space complexity.
- Include a short dry run when it helps explain the algorithm.
- For debugging, explain the root cause and show the corrected code.
- Never claim the code was executed or tested unless an execution tool actually did so.
- Preserve code, identifiers, operators, and numeric literals exactly during translation.
""".strip()

    if kind == "math":
        return common + """

MATHEMATICS DEFAULTS
- Solve the problem and put the final result clearly at the end (or first for simple arithmetic).
- Show concise, ordered steps for nontrivial problems.
- Keep equations on coherent lines; do not split their terms into bullets.
- Check arithmetic and verify the result when feasible.
- Include units where relevant. State assumptions if the problem is ambiguous.
""".strip()

    return common


def prepare_problem_request(question: str) -> dict[str, Any]:
    """
    Backend integration entry point.

    Returns:
      {"route": "deterministic", "answer": ...} for simple arithmetic; or
      {"route": "llm", "kind": ..., "system_prompt": ...} for other questions.
    """
    route = classify_problem(question)
    if route.kind == "math":
        result = calculate_simple_arithmetic(question)
        if result is not None:
            return {
                "route": "deterministic",
                "kind": "math",
                "answer": result["formatted_answer"],
                "details": result,
            }
    return {
        "route": "llm",
        "kind": route.kind,
        "system_prompt": specialist_system_prompt(route.kind),
    }


def normalize_llm_text(value: Any) -> str:
    """
    Safe boundary helper for the LLM response value.

    Prevents Python/JS structured objects from becoming '[object Object]'.
    Dict/list inputs are serialized as readable JSON, not stringified with str().
    Prefer passing a plain string from the LLM client in the first place.
    """
    import json

    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, indent=2, default=str)
    return str(value)
