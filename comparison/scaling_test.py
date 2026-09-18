# comparison/scaling_test.py
# Measures classical runtime empirically across database sizes N=8 to N=1,048,576.
# Quantum query count is computed analytically (floor(pi/4 * sqrt(N))).
# Produces the core comparison dataset saved as CSV.

import sys, os, time, random, math, csv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dna_encoder             import encode_sequence, get_num_qubits
from classical.linear_search import linear_search
from classical.kmp_search    import kmp_search
from classical.rabin_karp    import rabin_karp_search

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

BASES   = ['A', 'T', 'G', 'C']
SEQ_LEN = 4
TARGET  = "GTAC"

# Database sizes — powers of 2 for clean qubit math
SIZES = [8, 16, 32, 64, 128, 256, 512, 1024,
         2048, 4096, 16384, 65536, 262144, 1048576]

REPEATS = 5   # repeat each classical measurement N times, take median


def build_synthetic_db(n: int, seed: int = 42) -> list:
    """Build a synthetic DNA database of size n with target at the last position."""
    random.seed(seed)
    db = []
    for i in range(n - 1):
        seq = ''.join(random.choice(BASES) for _ in range(SEQ_LEN))
        db.append({
            "id": f"S{i:06d}", "name": f"Suspect_{i:06d}",
            "sequence": seq, "binary": encode_sequence(seq),
            "int_index": int(encode_sequence(seq), 2),
        })
    # Target always at the end — worst case for all classical algorithms
    db.append({
        "id": "STARGET", "name": "Suspect_TARGET",
        "sequence": TARGET, "binary": encode_sequence(TARGET),
        "int_index": int(encode_sequence(TARGET), 2),
    })
    return db


def measure_classical(db: list, target: str, func) -> tuple:
    """Run a classical search REPEATS times, return (median_ms, comparisons)."""
    times = []
    comparisons = 0
    for _ in range(REPEATS):
        res = func(db, target)
        times.append(res["time_ms"])
        comparisons = res["comparisons"]
    times.sort()
    return times[len(times) // 2], comparisons


def quantum_queries(n: int) -> int:
    """Optimal Grover iteration count for database size n."""
    return max(1, math.floor((math.pi / 4) * math.sqrt(n)))


def quantum_success_prob(n: int) -> float:
    """Theoretical success probability after optimal iterations."""
    k   = quantum_queries(n)
    theta = math.asin(1.0 / math.sqrt(n))
    return math.sin((2 * k + 1) * theta) ** 2


def run_scaling_test(verbose: bool = True) -> list:
    """
    Run the full scaling test across all database sizes.
    Returns list of row dicts, also saves CSV to results/.
    """
    if verbose:
        print("=" * 80)
        print("SCALING TEST — Classical O(N) vs Quantum O(sqrtN)")
        print(f"Target: '{TARGET}'  |  Worst-case placement (last record)")
        print("=" * 80)
        print(f"\n{'N':>10}  {'Qubits':>6}  {'Linear(ms)':>12}  {'KMP(ms)':>10}"
              f"  {'RK(ms)':>10}  {'Q.Queries':>10}  {'Speedup':>8}  {'Q.Prob%':>8}")
        print("-" * 80)

    rows = []

    for n in SIZES:
        db = build_synthetic_db(n)

        # Classical measurements (skip very large N for KMP/RK — too slow)
        lin_ms, lin_cmp = measure_classical(db, TARGET, linear_search)

        if n <= 65536:
            kmp_ms, kmp_cmp = measure_classical(db, TARGET, kmp_search)
            rk_ms,  rk_cmp  = measure_classical(db, TARGET, rabin_karp_search)
        else:
            kmp_ms = kmp_cmp = None
            rk_ms  = rk_cmp  = None

        q_queries = quantum_queries(n)
        q_prob    = quantum_success_prob(n)
        speedup   = n / q_queries       # classical worst / quantum queries
        qubits    = get_num_qubits(n)

        row = {
            "N":              n,
            "qubits":         qubits,
            "linear_ms":      round(lin_ms, 6),
            "linear_cmp":     lin_cmp,
            "kmp_ms":         round(kmp_ms, 6) if kmp_ms else "N/A",
            "kmp_cmp":        kmp_cmp if kmp_cmp else "N/A",
            "rk_ms":          round(rk_ms, 6) if rk_ms else "N/A",
            "rk_cmp":         rk_cmp if rk_cmp else "N/A",
            "quantum_queries": q_queries,
            "speedup_ratio":  round(speedup, 2),
            "quantum_prob":   round(q_prob * 100, 2),
        }
        rows.append(row)

        if verbose:
            kms  = f"{kmp_ms:.4f}" if kmp_ms else "   N/A"
            rms  = f"{rk_ms:.4f}"  if rk_ms  else "   N/A"
            print(f"{n:>10}  {qubits:>6}  {lin_ms:>12.4f}  {kms:>10}"
                  f"  {rms:>10}  {q_queries:>10}  {speedup:>8.1f}x  {q_prob*100:>7.2f}%")

    # Save CSV
    csv_path = os.path.join(RESULTS_DIR, "scaling_data.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    if verbose:
        print(f"\nCSV saved: {csv_path}")
        print(f"\nKey insight: At N=1,048,576 — classical needs {SIZES[-1]:,} comparisons,"
              f" quantum needs only {quantum_queries(SIZES[-1]):,} queries"
              f" ({SIZES[-1]/quantum_queries(SIZES[-1]):.0f}x speedup)")

    return rows


if __name__ == "__main__":
    run_scaling_test()