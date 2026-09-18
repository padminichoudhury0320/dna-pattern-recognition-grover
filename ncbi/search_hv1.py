# ncbi/search_hv1.py
# Runs classical + quantum search on the real NCBI HV1 database.
#
# IMPORTANT — two-level addressing:
#   Search KEY  : the 8-base HV1 window (e.g. "GAAGCAGA")
#   Quantum ADDRESS : sequential index 0-15 in the database list
#
# Grover searches over 16 indices (4 qubits, k=3 iterations).
# When it returns index i, we look up db[i] to get the real accession.
# This is the correct architecture — analogous to how a real database
# uses row IDs, not content hashes, as primary keys.
import random
import sys, os, math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ncbi.hv1_database          import build_hv1_database,    get_hv1_target
from classical.linear_search    import linear_search
from classical.kmp_search       import kmp_search
from classical.rabin_karp       import rabin_karp_search
from quantum.grover             import build_grover_circuit, optimal_iterations
from quantum.simulator          import run_statevector, run_qasm


def run_hv1_search():
    db     = build_hv1_database(use_cache=True)
    target_record = random.choice(db)

    target = {
        "sequence": target_record["sequence"],
        "binary": target_record["binary"],
        "int_index": target_record["int_index"],
        "source": "Crime scene HV1 sample"
    }
    N      = len(db)
    if (N & (N - 1)) != 0:
        raise ValueError(
            f"Database size {N} is not a power of two. "
            f"Grover implementation expects N = 2^n."
    )
    print("\nDatabase Records")
    print("-" * 68)

    for i, rec in enumerate(db):
        print(
            f"{i:02d} | "
            f"{rec['id']:<15} | "
            f"{rec['sequence']}"
        )

    print("=" * 68)
    print("PHASE 6 — SEARCH ON REAL NCBI HV1 DATABASE")
    print(f"Database : {N} real human mitochondrial DNA sequences (NCBI GenBank)")
    print(f"Target   : {target['sequence']}  (HV1 window from crime scene sample)")
    print(
        f"Source   : "
        f"{target_record['id']} — "
        f"{target_record['description'][:50]}"
    )
    print("=" * 68)

    # ── Classical search ──────────────────────────────────────────────────
    # Classical algorithms compare HV1 windows directly
    print(f"\n── Classical search (comparing 8-base HV1 windows) ──")
    print(f"\n{'Method':<22} {'Found':<12} {'Correct':>8} "
          f"{'Queries':>9} {'Time (ms)':>12}")
    print("-" * 68)

    classical_results = []
    for name, func in [
        ("Linear Search",  linear_search),
        ("KMP Search",     kmp_search),
        ("Rabin-Karp",     rabin_karp_search),
    ]:
        res     = func(db, target["sequence"])
        found   = res["found"]["sequence"] if res["found"] else "NOT FOUND"
        correct = found == target["sequence"]
        classical_results.append(res)
        print(f"{name:<22} {found:<12} {'YES' if correct else 'NO':>8} "
              f"{res['comparisons']:>9} {res['time_ms']:>12.4f}")

    # ── Quantum search ────────────────────────────────────────────────────
    # Quantum circuit uses sequential index (0 to N-1), not the binary window value.
    # This is the correct architecture: 4 qubits for 16 records, k=3 iterations.
    print(f"\n── Quantum search (Grover's algorithm) ──")

    num_qubits = math.ceil(math.log2(N))   # = 4 for N=16
    k          = optimal_iterations(N)      # = 3 for N=16

    # Find the sequential index of the target in the database list
    target_idx = next(
        (i for i, r in enumerate(db) if r["sequence"] == target["sequence"]),
        None
    )
    target_bits = format(target_idx, f'0{num_qubits}b')

    print(f"\n  Database size N    : {N}")
    print(f"  Qubits (log2 N)    : {num_qubits}  →  {2**num_qubits} addressable states")
    print(f"  Target record      : index {target_idx}  →  |{target_bits}⟩")
    print(f"  Target accession   : {db[target_idx]['id']}")
    print(f"  Target HV1 window  : {db[target_idx]['sequence']}")
    print(f"  Grover iterations k: {k}  [floor(π/4 · √{N})]")

    # Build and run the Grover circuit
    grover_qc   = build_grover_circuit(target_idx, num_qubits, N, iterations=k)
    sv_result   = run_statevector(grover_qc, num_qubits)
    qasm_result = run_qasm(grover_qc, shots=1024)

    # Interpret results
    sv_prob  = sv_result["probabilities"].get(target_bits, 0)
    theta = math.asin(1 / math.sqrt(N))

    expected_prob = (
        math.sin((2 * k + 1) * theta)
    ) ** 2
    top_bits = max(qasm_result["counts"], key=qasm_result["counts"].get)
    top_count= qasm_result["counts"][top_bits]
    top_idx  = int(top_bits, 2)
    top_rec  = db[top_idx] if 0 <= top_idx < len(db) else None
    correct_q= top_bits == target_bits
    print(
    f"  Theoretical probability : "
    f"{expected_prob*100:.2f}%"
    )

    print(
        f"  Observed probability    : "
        f"{sv_prob*100:.2f}%"
    )

    print(
        f"  Difference              : "
        f"{abs(expected_prob-sv_prob)*100:.4f}%"
    )

    print(f"\n  ── Statevector (exact) ──")
    print(f"  Target |{target_bits}⟩ probability : {sv_prob*100:.2f}%")
    print(f"  All other states sum        : {(1-sv_prob)*100:.2f}%")

    print(f"\n  ── QASM (1024 shots) ──")
    print(f"  Top measured state : |{top_bits}⟩  ({top_count}/1024 shots = {top_count/1024*100:.1f}%)")
    print(f"  Maps to index      : {top_idx}")
    print(f"  Maps to accession  : {top_rec['id'] if top_rec else 'UNKNOWN'}")
    print(f"  Maps to window     : {top_rec['sequence'] if top_rec else 'UNKNOWN'}")
    print(f"  Correct match      : {'YES ✓' if correct_q else 'NO ✗'}")

    # ── Comparison summary ────────────────────────────────────────────────
    print(f"\n── Summary ──")
    print(f"\n{'Method':<22} {'Result':<12} {'Correct':>8} "
          f"{'Queries':>9}  Notes")
    print("-" * 68)
    for name, res in zip(
        ["Linear Search", "KMP Search", "Rabin-Karp"],
        classical_results
    ):
        found   = res["found"]["sequence"] if res["found"] else "NOT FOUND"
        correct = found == target["sequence"]
        complexities = {
            "Linear Search": "O(N)",
            "KMP Search": "O(N+M)",
            "Rabin-Karp": "O(N+M)"
        }

        print(
            f"{name:<22} "
            f"{found:<12} "
            f"{'YES' if correct else 'NO':>8} "
            f"{res['comparisons']:>9}  "
            f"{complexities[name]}"
        )
    print(f"{'Grover (Quantum)':<22} "
          f"{(top_rec['sequence'] if top_rec else 'NOT FOUND'):<12} "
          f"{'YES' if correct_q else 'NO':>8} "
          f"{k:>9}  O(√N)")

    print(f"\nQuantum speedup on real NCBI data:")
    print(f"  Classical worst case : {N} comparisons")
    print(f"  Grover queries used  : {k}")
    print("\nComplexity Analysis")

    print(
        f"  Classical complexity : O(N)"
    )

    print(
        f"  Quantum complexity   : O(√N)"
    )

    print(
        f"  Classical worst case : {N} comparisons"
    )

    print(
        f"  Grover iterations    : {k}"
    )

    print(
        f"  Reduction factor     : {N/k:.1f}×"
    )
    print(f"  Success probability  : {sv_prob*100:.2f}%  (statevector exact)")
    print(f"\nAll {N} database records are citable NCBI GenBank accessions.")
    print(f"Target accession: {db[target_idx]['id']}")
    print("\nForensic Interpretation")
    print("-" * 68)

    print(
        f"The crime-scene HV1 sample "
        f"matched accession "
        f"{db[target_idx]['id']}."
    )

    print(
        f"The matching HV1 window was "
        f"{db[target_idx]['sequence']}."
    )

    print(
        f"Classical algorithms required "
        f"up to {N} comparisons."
    )

    print(
        f"Grover's algorithm required "
        f"only {k} oracle iterations."
    )

    print(
        "This demonstrates how quantum "
        "search can accelerate future "
        "forensic DNA database searches."
    )


if __name__ == "__main__":
    run_hv1_search()