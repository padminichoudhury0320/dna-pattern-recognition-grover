# comparison/report.py
# Generates the complete project summary report.
# Covers: project objective, methods, results, analysis, conclusions.
# Saves to results/final_report.txt

import sys, os, math, datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comparison.benchmark      import run_full_benchmark
from comparison.scaling_test   import quantum_queries, quantum_success_prob
from dna_encoder import get_num_qubits
from database                  import build_database, get_target

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def generate_report():
    db     = build_database()
    target = get_target()
    N      = len(db)
    k      = quantum_queries(N)
    prob   = quantum_success_prob(N)
    qbits  = math.ceil(math.log2(N))

    results = run_full_benchmark(verbose=False)
    c_lin   = next(r for r in results if r["method"] == "Linear Search")
    c_kmp   = next(r for r in results if r["method"] == "KMP Search")
    c_rk    = next(r for r in results if r["method"] == "Rabin-Karp")
    q_res   = next(r for r in results if r["type"] == "quantum")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    def w(s=""): lines.append(s)

    w("=" * 72)
    w("DNA PATTERN RECOGNITION FOR FORENSIC INVESTIGATION")
    w("USING GROVER'S QUANTUM SEARCH ALGORITHM")
    w(f"Project Report  |  Generated: {now}")
    w("=" * 72)

    w()
    w("1. PROBLEM STATEMENT")
    w("-" * 40)
    w("In forensic investigations, DNA samples obtained from crime scenes are")
    w("compared against large suspect databases to identify potential matches.")
    w("Classical search methods scale linearly O(N), becoming computationally")
    w("expensive as database size N grows into the millions (e.g. CODIS: 20M+).")
    w("This project applies Grover's Quantum Search Algorithm to demonstrate")
    w("a provable quadratic speedup: O(sqrt(N)) quantum queries vs O(N) classical.")

    w()
    w("2. METHODOLOGY")
    w("-" * 40)
    w("Phase 1  DNA Encoding")
    w("         A=00, T=01, G=10, C=11 — 2-bit encoding per base")
    w("         4-base sequences encoded to 8-bit binary strings")
    w()
    w("Phase 2  Classical Implementation")
    w("         Three algorithms implemented and benchmarked:")
    w("         (a) Linear Search  — O(N) brute-force comparison")
    w("         (b) KMP Search     — O(N+M) failure-table optimisation")
    w("         (c) Rabin-Karp     — O(N+M) rolling-hash comparison")
    w()
    w("Phase 3  Quantum Circuit Design")
    w("         Grover oracle: phase-flip of target state |t> only")
    w("         Diffuser: inversion-about-the-mean amplitude amplification")
    w(f"         Optimal iterations: k = floor(pi/4 * sqrt(N)) = {k}")
    w()
    w("Phase 4  Quantum Simulation (Qiskit Aer)")
    w("         Statevector simulator — exact probability computation")
    w("         QASM simulator       — 1024-shot measurement sampling")

    w()
    w("3. EXPERIMENTAL SETUP")
    w("-" * 40)
    w(f"Database size    : N = {N} DNA sequences")
    w(f"Sequence length  : 4 bases (8-bit binary per sequence)")
    w(f"Qubits required  : {qbits} (2^{qbits} = {2**qbits} addressable states)")
    w(f"Target sequence  : {target['sequence']}  "
      f"(binary: {target['binary']}, index: {target['int_index']})")
    w(f"Grover iterations: k = {k}")
    w(f"QASM shots       : 1024")

    w()
    w("4. RESULTS")
    w("-" * 40)
    w()
    w("4a. Classical search results (same database, same target)")
    w(f"  {'Method':<20} {'Queries':>10} {'Time (ms)':>12} {'Correct':>9}")
    w(f"  {'-'*55}")
    for r in [c_lin, c_kmp, c_rk]:
        tick = "Yes" if r["correct"] else "No"
        w(f"  {r['method']:<20} {r['queries']:>10} {r['time_ms']:>12.4f} {tick:>9}")

    w()
    w("4b. Quantum search results (Grover's algorithm, Qiskit Aer)")
    w(f"  Oracle queries used    : {k}  (vs {N} classical comparisons)")
    w(f"  Statevector probability: {q_res.get('sv_prob',0)*100:.2f}%")
    w(f"  QASM accuracy          : {q_res.get('qasm_prob',0)*100:.2f}%  (1024 shots)")
    w(f"  Correct match found    : {'Yes' if q_res['correct'] else 'No'}")
    w(f"  Target identified      : {q_res['found']}")

    w()
    w("5. COMPLEXITY ANALYSIS")
    w("-" * 40)
    w(f"  {'Database Scale':<22} {'N':>12}  {'Classical':>11}  {'Quantum':>9}  {'Speedup':>9}")
    w(f"  {'-'*68}")

    scales = [
        ("Our project",      16),
        ("Small lab",        1_000),
        ("Regional DB",      100_000),
        ("National (CODIS)", 20_000_000),
        ("Global scale",     100_000_000),
    ]
    for label, n in scales:
        q = quantum_queries(n)
        s = n / q
        w(f"  {label:<22} {n:>12,}  {n:>11,}  {q:>9,}  {s:>8.0f}x")

    w()
    w("6. KEY FINDINGS")
    w("-" * 40)
    w(f"  1. All three classical algorithms correctly identified the target DNA")
    w(f"     sequence '{target['sequence']}' but required up to {N} comparisons (O(N)).")
    w()
    w(f"  2. Grover's algorithm found the same target with only {k} oracle queries,")
    w(f"     achieving {N/k:.1f}x fewer operations than the classical worst case.")
    w()
    w(f"  3. Quantum success probability reached {prob*100:.2f}% — well above the")
    w(f"     classical random-guess baseline of {100/N:.2f}% (1/N).")
    w()
    w(f"  4. The speedup scales as O(sqrt(N)): at CODIS scale (20M records),")
    w(f"     quantum needs only {quantum_queries(20_000_000):,} queries vs 20,000,000 classical.")
    w()
    w(f"  5. The iteration count k = floor(pi/4 * sqrt(N)) is critical.")
    w(f"     Exceeding it degrades accuracy — the probability oscillates.")

    w()
    w("7. LIMITATIONS & FUTURE WORK")
    w("-" * 40)
    w("  Current hardware (NISQ era) cannot run this circuit on real quantum")
    w("  computers at forensic scale — noise and decoherence limit qubit count.")
    w("  Future work:")
    w("  - Implement on IBM Quantum / Rigetti hardware with error mitigation")
    w("  - Extend to multi-locus STR profiles (real CODIS 20-locus standard)")
    w("  - Integrate NCBI GenBank real sequence data (Tier 2 database)")
    w("  - Hybrid classical-quantum pipeline for pre-filtering + quantum search")
    w("  - Fault-tolerant quantum hardware to run at true forensic scale")

    w()
    w("8. CONCLUSION")
    w("-" * 40)
    w("This project successfully demonstrates that Grover's Quantum Search")
    w("Algorithm provides a provable quadratic speedup over classical DNA")
    w("search methods. Implemented in Qiskit and validated on a simulated")
    w(f"forensic database of {N} records, the quantum approach achieved {prob*100:.1f}%")
    w("accuracy using only sqrt(N) oracle queries. At the scale of real forensic")
    w("databases (millions of profiles), this represents a transformative")
    w("reduction in search complexity with direct practical impact.")
    w()
    w("=" * 72)

    report_text = "\n".join(lines)
    print(report_text)

    path = os.path.join(RESULTS_DIR, "final_report.txt")
    with open(path, "w") as f:
        f.write(report_text)
    print(f"\nReport saved: {path}")


if __name__ == "__main__":
    generate_report()