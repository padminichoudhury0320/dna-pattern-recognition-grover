# comparison/benchmark.py
# Head-to-head benchmark: all three classical algorithms + Grover's quantum search.
# Runs on the same 16-record database, same target, same conditions.
# Records time, comparisons/queries, and correctness for every method.

import sys, os, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database                import build_database, get_target
from classical.linear_search import linear_search
from classical.kmp_search    import kmp_search
from classical.rabin_karp    import rabin_karp_search
from quantum.simulator       import full_grover_search
from dna_encoder             import get_num_qubits
import math


def run_full_benchmark(verbose: bool = True) -> list:
    """
    Run all four search methods on the same database and target.
    Returns a list of result dicts for further analysis.
    """
    db     = build_database()
    target = get_target()
    N      = len(db)
    k      = math.floor((math.pi / 4) * math.sqrt(N))

    if verbose:
        print("=" * 68)
        print("PHASE 5 — CLASSICAL vs QUANTUM BENCHMARK")
        print(f"Database : {N} DNA records  |  Target : {target['sequence']}")
        print("=" * 68)

    results = []

    # ── Classical methods ────────────────────────────────────────────────
    classical_methods = [
        ("Linear Search",  linear_search,       f"O(N)     worst={N}"),
        ("KMP Search",     kmp_search,           f"O(N+M)   worst={N}"),
        ("Rabin-Karp",     rabin_karp_search,    f"O(N+M)   worst={N}"),
    ]

    for name, func, complexity in classical_methods:
        res    = func(db, target["sequence"])
        found  = res["found"]["sequence"] if res["found"] else "NOT FOUND"
        correct = found == target["sequence"]
        results.append({
            "method":      name,
            "type":        "classical",
            "found":       found,
            "correct":     correct,
            "queries":     res["comparisons"],
            "time_ms":     res["time_ms"],
            "complexity":  complexity,
        })

    # ── Quantum method ───────────────────────────────────────────────────
    qr      = full_grover_search()
    top     = qr["top_result"]
    qfound  = top["record"]["sequence"] if top and top["record"] else "NOT FOUND"
    qcorrect = qfound == target["sequence"]
    qtime    = qr["statevector"]["elapsed_ms"] + qr["qasm"]["elapsed_ms"]

    results.append({
        "method":     "Grover (Quantum)",
        "type":       "quantum",
        "found":      qfound,
        "correct":    qcorrect,
        "queries":    k,               # Grover uses k oracle queries
        "time_ms":    qtime,
        "complexity": f"O(sqrtN)  k={k}",
        "sv_prob":    qr["statevector"]["probabilities"].get(
                          format(qr["target_idx"], f'0{qr["num_qubits"]}b'), 0),
        "qasm_prob":  top["probability"] if top else 0,
    })

    if verbose:
        _print_results_table(results, target, N, k)

    return results


def _print_results_table(results, target, N, k):
    print(f"\n{'Method':<22} {'Found':<8} {'Correct':>8} {'Queries':>9}"
          f" {'Time (ms)':>10}  Complexity")
    print("-" * 68)

    for r in results:
        tick = "YES" if r["correct"] else "NO"
        print(f"{r['method']:<22} {r['found']:<8} {tick:>8} "
              f"{r['queries']:>9} {r['time_ms']:>10.4f}  {r['complexity']}")

    print()
    print(f"Theoretical speedup  : O(N) / O(sqrtN) = sqrt({N}) = {math.sqrt(N):.2f}x")
    print(f"Queries saved        : {N} → {k}  "
          f"({(N - k) / N * 100:.1f}% fewer oracle calls)")

    q_res = next(r for r in results if r["type"] == "quantum")
    print(f"Quantum accuracy     : statevector {q_res.get('sv_prob',0)*100:.2f}%"
          f"  |  QASM {q_res.get('qasm_prob',0)*100:.2f}%")


if __name__ == "__main__":
    run_full_benchmark()