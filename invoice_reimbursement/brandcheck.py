"""Brand/name guard. Blocked names are stored only as SHA-256 hashes, never
as plain text, so the blocklist itself cannot leak the names it guards.
Checking hashes word n-grams (up to 4 words) of normalised input text.
"""

from __future__ import annotations

import hashlib
import re

_WORD = re.compile(r"[a-z0-9]+")


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Hashes of names this repo must never present as its own or affiliate with.
# Hashes only, produced once offline; the plain names appear nowhere here.
BLOCKED_HASHES = frozenset({
    "c952a08fdb0ff916b78a489ff321a4eb73d258612ededdd834c5a7c55fbc6c70",
    "17e9b17189f2f67e00b4c8dce8a6bedb38051ee221602fd52c88650ef9f68687",
    "b8cf8815b888e70296256f5f85780fedcffe5001dbae3377e9e3ebb1d33e206b",
    "f2a21b0e077c1aea6c1641d9b2c6165575488732b51c9868976a904464681352",
})


def _ngrams(words: list, max_n: int = 4):
    for n in range(1, max_n + 1):
        for i in range(len(words) - n + 1):
            yield " ".join(words[i:i + n])


def find_blocked(text: str) -> list:
    """Return the list of blocked-name hashes found in text (empty = clean)."""
    words = _WORD.findall(str(text).lower())
    return [h for h in (_hash(g) for g in _ngrams(words)) if h in BLOCKED_HASHES]


def is_clean(text: str) -> bool:
    return not find_blocked(text)
