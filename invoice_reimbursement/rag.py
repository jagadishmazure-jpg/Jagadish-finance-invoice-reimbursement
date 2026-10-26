"""Deterministic retrieval over the synthetic policy rulebook.

This is a keyword-overlap retriever, not a hosted model: it scores each
passage by shared terms with the query, so the governing passage for a
decision is reproducible and auditable. No network call is made.
"""

from __future__ import annotations

import re
from pathlib import Path

_WORD = re.compile(r"[a-z0-9]+")


def _terms(text: str) -> set:
    """Terms plus a light reimbursement/reimbursed synonym expansion, so a
    query about reimbursement matches passages written with reimbursed."""
    terms = set(_WORD.findall(text.lower()))
    expanded = set(terms)
    for term in terms:
        if term.endswith("ment"):
            expanded.add(term[:-4] + "ed")
        if term.endswith("ed"):
            expanded.add(term[:-2] + "ment")
    return expanded


def load_passages(path: Path | None = None) -> list:
    """Load rulebook passages from data/policy_rulebook.md (rule id per block)."""
    if path is None:
        path = Path(__file__).resolve().parent.parent / "data" / "policy_rulebook.md"
    passages = []
    current_id, current_lines = None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if current_id is not None:
                passages.append({"rule_id": current_id,
                                 "text": " ".join(current_lines).strip()})
            current_id = line[3:].strip()
            current_lines = []
        elif line.strip():
            current_lines.append(line.strip())
    if current_id is not None:
        passages.append({"rule_id": current_id,
                         "text": " ".join(current_lines).strip()})
    return passages


def retrieve(query: str, passages: list, top_k: int = 3,
             boost_terms: set | None = None) -> list:
    """Return the top_k passages ranked by term overlap (plus a bonus for
    boost terms, e.g. the claim category), then by rule id."""
    query_terms = _terms(query)
    boost_terms = boost_terms or set()
    scored = []
    for passage in passages:
        passage_terms = _terms(passage["text"])
        overlap = len(query_terms & passage_terms)
        overlap += 2 * len(boost_terms & passage_terms)
        scored.append((overlap, passage["rule_id"], passage))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [item[2] for item in scored[:top_k] if item[0] > 0]
