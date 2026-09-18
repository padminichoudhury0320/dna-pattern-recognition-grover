# classical/linear_search.py
# Brute-force DNA search. Checks every database record one by one.
# Complexity: O(N) time, O(1) extra space.
# This is our purest baseline — no optimisation at all.

import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dna_encoder import encode_sequence


def linear_search(database: list, target_sequence: str) -> dict:
    """
    Search the database for a DNA sequence using linear (brute-force) search.

    How it works:
      - Encode the target sequence to binary once.
      - Loop through every record in the database.
      - Compare its binary encoding to the target binary.
      - Return the first match found.

    Returns a result dict with match info, comparison count, and timing.
    """
    target_binary = encode_sequence(target_sequence)

    comparisons = 0
    start_time  = time.perf_counter()

    found = None
    for record in database:
        comparisons += 1
        if record["binary"] == target_binary:
            found = record
            break                           # stop as soon as we find it

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    return {
        "method":      "Linear Search",
        "target":      target_sequence,
        "found":       found,
        "comparisons": comparisons,
        "time_ms":     elapsed_ms,
        "complexity":  "O(N)",
    }


def linear_search_all(database: list, target_sequence: str) -> dict:
    """
    Variant: does NOT stop at first match.
    Useful when the database might have duplicates (real forensic scenario).
    """
    target_binary = encode_sequence(target_sequence)

    comparisons = 0
    matches     = []
    start_time  = time.perf_counter()

    for record in database:
        comparisons += 1
        if record["binary"] == target_binary:
            matches.append(record)

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    return {
        "method":      "Linear Search (all matches)",
        "target":      target_sequence,
        "found":       matches[0] if matches else None,
        "all_matches": matches,
        "comparisons": comparisons,
        "time_ms":     elapsed_ms,
        "complexity":  "O(N)",
    }


# ── Self-test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database import build_database, get_target

    db     = build_database()
    target = get_target()

    print("=" * 55)
    print("LINEAR SEARCH — SELF TEST")
    print("=" * 55)

    result = linear_search(db, target["sequence"])

    print(f"Target     : {result['target']}")
    print(f"Found      : {result['found']['name'] if result['found'] else 'NOT FOUND'}")
    print(f"Comparisons: {result['comparisons']} out of {len(db)}")
    print(f"Time       : {result['time_ms']:.4f} ms")
    print(f"Complexity : {result['complexity']}")

    # Test with a sequence NOT in the database
    result_miss = linear_search(db, "CCCA")
    print(f"\nMiss test  : searching 'CCCA' -> {'NOT FOUND' if not result_miss['found'] else 'FOUND'}")
    print(f"Comparisons: {result_miss['comparisons']} (scanned full DB)")