# RAG and policy design (knowledge note)

## Why the rulebook is prose plus code

A finance decision needs two things that one representation cannot give
alone: a machine-checkable rule (is $600 over a $500 cap?) and a
human-readable passage (what does the rule actually say?). This repo
keeps both, linked by a stable rule id. The prose file is what retrieval
searches; the code module is what enforcement checks. Drift between them
is the known risk, and the implementation guide tells adopters to test
for agreement.

## Why keyword retrieval is enough here

The rulebook has seven passages. With a corpus that small, term overlap
plus a category bonus ranks the governing passage first in every tested
case, deterministically, with no model, no embeddings, and no network.
Semantic retrieval would add machinery without changing any decision in
this corpus. The interface (`retrieve(query, passages, top_k,
boost_terms)`) is the seam where a stronger retriever would plug in
later, without touching the pipeline.

## Why retrieval results are stored, not just shown

A decision shown once and forgotten cannot be audited. The pipeline
stores retrieved passage ids on the decision record, next to the rule
citations, so a later reviewer can re-fetch the exact passages that
justified the outcome — even if the rulebook has since changed.
