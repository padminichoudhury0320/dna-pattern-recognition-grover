# comparison/complexity_analysis.py
# Computes and displays theoretical complexity comparison at forensic scale.
# Covers: our project DB, regional DB, national DB (CODIS-scale), global DB.

import sys, os, math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FORENSIC_SCALES = [
    ("Our project DB",      16,         "simulated, 16 records"),
    ("Small lab DB",        1_000,      "small forensic lab"),
    ("Regional DB",         100_000,    "state/regional forensic DB"),
    ("National DB",         20_000_000, "CODIS (US national DB)"),
    ("Global DB",           100_000_000,"Interpol-scale estimate"),
]

def grover_queries(n):    return max(1, math.floor((math.pi/4) * math.sqrt(n)))
def success_prob(n):
    k = grover_queries(n)
    theta = math.asin(1.0 / math.sqrt(n))
    return math.sin((2*k+1)*theta)**2
def qubits_needed(n):     return math.ceil(math.log2(n))


def run_complexity_analysis():
    print("=" * 78)
    print("COMPLEXITY ANALYSIS — Classical O(N) vs Grover O(sqrt N) at Forensic Scale")
    print("=" * 78)

    print(f"\n{'Scale':<22} {'N':>12}  {'Classical':>12}  {'Quantum':>9}"
          f"  {'Speedup':>9}  {'Qubits':>7}  {'Q.Prob%':>8}")
    print("-" * 78)

    for label, n, note in FORENSIC_SCALES:
        classical = n                  # worst-case linear scan
        quantum   = grover_queries(n)
        speedup   = classical / quantum
        qbits     = qubits_needed(n)
        prob      = success_prob(n)

        print(f"{label:<22} {n:>12,}  {classical:>12,}  {quantum:>9,}"
              f"  {speedup:>8.0f}x  {qbits:>7}  {prob*100:>7.2f}%")
        print(f"  {'':22} ({note})")

    print()
    print("Interpretation:")
    print("  Classical: worst case requires scanning EVERY record once.")
    print("  Quantum  : Grover finds the answer in O(sqrt N) oracle queries.")
    print("  Speedup  : quantum / classical ratio grows as sqrt(N).")
    print()

    # Extra: show how speedup scales
    print(f"  {'N':>12}  {'Speedup':>10}  {'Qubits':>8}")
    print(f"  {'-'*34}")
    for exp in range(3, 28):
        n = 2**exp
        q = grover_queries(n)
        s = n / q
        b = qubits_needed(n)
        if exp in [3,4,6,8,10,14,18,24]:
            print(f"  {n:>12,}  {s:>9.0f}x  {b:>8} qubits")


if __name__ == "__main__":
    run_complexity_analysis()