# classical/kmp_search.py
# Knuth-Morris-Pratt pattern matching on binary-encoded DNA sequences.
# Complexity: O(N + M) where N = total text length, M = pattern length.
#
# Key idea: Build a "failure function" (also called partial match table)
# from the pattern. When a mismatch occurs mid-comparison, instead of
# restarting from scratch, jump back only as far as the table says.

import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dna_encoder import encode_sequence


def _build_failure_table(pattern: str) -> list:
    """
    Build the KMP failure (partial match) table for a given pattern.

    The table[i] stores the length of the longest proper prefix of
    pattern[0..i] that is also a suffix. This lets us skip redundant
    comparisons on mismatch.

    Example for pattern '00011011' (ATGC):
      Index:   0  1  2  3  4  5  6  7
      Pattern: 0  0  0  1  1  0  1  1
      Table:   0  1  2  0  0  1  0  1
    """
    m     = len(pattern)
    table = [0] * m
    length = 0          # length of previous longest prefix-suffix
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            table[i] = length
            i += 1
        else:
            if length != 0:
                length = table[length - 1]   # don't increment i here
            else:
                table[i] = 0
                i += 1

    return table


def _kmp_match(text: str, pattern: str, failure_table: list) -> tuple:
    """
    Run KMP search on a single text string against the pattern.
    Returns (matched: bool, comparisons_made: int).
    """
    n = len(text)
    m = len(pattern)

    i = 0               # index into text
    j = 0               # index into pattern
    comparisons = 0

    while i < n:
        comparisons += 1
        if text[i] == pattern[j]:
            i += 1
            j += 1
        else:
            if j != 0:
                j = failure_table[j - 1]    # jump using failure table
            else:
                i += 1

        if j == m:
            return True, comparisons        # full match found

    return False, comparisons


def kmp_search(database: list, target_sequence: str) -> dict:
    """
    Search the database using KMP.

    Steps:
      1. Encode the target sequence to binary (this is the pattern).
      2. Build the failure table from the pattern — done once, O(M).
      3. For each database record, run KMP match on its binary string.
      4. Return first match with accumulated comparison count.
    """
    target_binary = encode_sequence(target_sequence)
    failure_table = _build_failure_table(target_binary)

    total_comparisons = 0
    start_time        = time.perf_counter()

    found = None
    for record in database:
        matched, comps = _kmp_match(record["binary"], target_binary, failure_table)
        total_comparisons += comps
        if matched:
            found = record
            break

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    return {
        "method":        "KMP Search",
        "target":        target_sequence,
        "found":         found,
        "comparisons":   total_comparisons,
        "time_ms":       elapsed_ms,
        "complexity":    "O(N + M)",
        "failure_table": failure_table,
    }


# ── Self-test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from database import build_database, get_target

    db     = build_database()
    target = get_target()

    print("=" * 55)
    print("KMP SEARCH — SELF TEST")
    print("=" * 55)

    result = kmp_search(db, target["sequence"])

    pattern_binary = encode_sequence(target["sequence"])
    ft = _build_failure_table(pattern_binary)

    print(f"Target        : {result['target']}")
    print(f"Pattern binary: {pattern_binary}")
    print(f"Failure table : {ft}")
    print(f"Found         : {result['found']['name'] if result['found'] else 'NOT FOUND'}")
    print(f"Comparisons   : {result['comparisons']}")
    print(f"Time          : {result['time_ms']:.4f} ms")
    print(f"Complexity    : {result['complexity']}")

    result_miss = kmp_search(db, "CCCA")
    print(f"\nMiss test     : 'CCCA' -> {'NOT FOUND' if not result_miss['found'] else 'FOUND'}")
    print(f"Comparisons   : {result_miss['comparisons']}")