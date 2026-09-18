# classical/rabin_karp.py
# Rabin-Karp rolling hash pattern matching on binary-encoded DNA.
# Average complexity: O(N + M). Worst case O(NM) if many hash collisions.
#
# Key idea: Instead of comparing strings character by character every time,
# compute a numeric "fingerprint" (hash) for the pattern and for each
# window of the same length in the text. Only do a full string comparison
# when fingerprints match — which is rare unless there's a real match.

import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dna_encoder import encode_sequence

# Rabin-Karp parameters
BASE  = 4       # base for polynomial hash (4 chars: 0,1 in binary, but we treat each char)
PRIME = 101     # a prime number to reduce hash collisions


def _hash(string: str, length: int) -> int:
    """Compute the initial polynomial hash for the first window."""
    h = 0
    for i in range(length):
        h = (h * BASE + ord(string[i])) % PRIME
    return h


def _rabin_karp_match(text: str, pattern: str) -> tuple:
    """
    Run Rabin-Karp on a single text string.
    Returns (matched: bool, comparisons_made: int).

    The rolling hash update formula:
      new_hash = (BASE * (old_hash - ord(leaving_char) * h_power) + ord(new_char)) % PRIME
    where h_power = BASE^(M-1) % PRIME
    """
    n = len(text)
    m = len(pattern)
    comparisons = 0

    if n < m:
        return False, 0

    # Precompute BASE^(M-1) % PRIME — used to remove leading character from hash
    h_power = 1
    for _ in range(m - 1):
        h_power = (h_power * BASE) % PRIME

    pattern_hash = _hash(pattern, m)
    window_hash  = _hash(text, m)

    for i in range(n - m + 1):
        comparisons += 1                        # count each window check

        if pattern_hash == window_hash:
            # Hash match — verify character by character to rule out collision
            if text[i:i + m] == pattern:
                return True, comparisons        # confirmed real match

        # Roll the hash forward (remove leftmost char, add new right char)
        if i < n - m:
            window_hash = (
                BASE * (window_hash - ord(text[i]) * h_power) + ord(text[i + m])
            ) % PRIME
            if window_hash < 0:
                window_hash += PRIME

    return False, comparisons


def rabin_karp_search(database: list, target_sequence: str) -> dict:
    """
    Search the database using Rabin-Karp rolling hash.

    Steps:
      1. Encode target to binary (the pattern).
      2. For each record, run Rabin-Karp on its binary string.
      3. Return first match with total comparison count.
    """
    target_binary     = encode_sequence(target_sequence)
    total_comparisons = 0
    start_time        = time.perf_counter()

    found = None
    for record in database:
        matched, comps = _rabin_karp_match(record["binary"], target_binary)
        total_comparisons += comps
        if matched:
            found = record
            break

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    return {
        "method":      "Rabin-Karp Search",
        "target":      target_sequence,
        "found":       found,
        "comparisons": total_comparisons,
        "time_ms":     elapsed_ms,
        "complexity":  "O(N + M) avg",
    }


# ── Self-test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from database import build_database, get_target

    db     = build_database()
    target = get_target()

    print("=" * 55)
    print("RABIN-KARP SEARCH — SELF TEST")
    print("=" * 55)

    result = rabin_karp_search(db, target["sequence"])

    print(f"Target     : {result['target']}")
    print(f"Found      : {result['found']['name'] if result['found'] else 'NOT FOUND'}")
    print(f"Comparisons: {result['comparisons']}")
    print(f"Time       : {result['time_ms']:.4f} ms")
    print(f"Complexity : {result['complexity']}")

    result_miss = rabin_karp_search(db, "CCCA")
    print(f"\nMiss test  : 'CCCA' -> {'NOT FOUND' if not result_miss['found'] else 'FOUND'}")
    print(f"Comparisons: {result_miss['comparisons']}")