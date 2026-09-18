# comparison/charts.py
# Generates 4 publication-quality comparison charts saved to results/.
#   1. Runtime vs N (classical algorithms, log scale)
#   2. Queries vs N (classical O(N) vs quantum O(sqrt N))
#   3. Speedup ratio vs N
#   4. Success probability vs N (quantum)

import sys, os, math
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comparison.scaling_test import run_scaling_test, quantum_queries, quantum_success_prob

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

BLUE   = '#378ADD'
CORAL  = '#D85A30'
TEAL   = '#1D9E75'
PURPLE = '#7F77DD'
GRAY   = '#888780'


def _save(fig, name):
    path = os.path.join(RESULTS_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    print(f"  Saved: {path}")
    plt.close(fig)


def chart1_runtime(rows):
    """Classical runtime (ms) vs N on log-log scale."""
    ns     = [r["N"] for r in rows if r["linear_ms"] != "N/A"]
    lin_ms = [r["linear_ms"] for r in ns and rows if r["linear_ms"] != "N/A"]

    ns     = [r["N"]         for r in rows]
    lin_ms = [r["linear_ms"] for r in rows]

    kmp_ns = [r["N"]      for r in rows if r["kmp_ms"] != "N/A"]
    kmp_ms = [r["kmp_ms"] for r in rows if r["kmp_ms"] != "N/A"]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.loglog(ns, lin_ms, 'o-', color=BLUE,   lw=2, ms=5, label='Linear search O(N)')
    ax.loglog(kmp_ns, kmp_ms, 's--', color=TEAL, lw=2, ms=5, label='KMP O(N+M)')

    ax.set_xlabel("Database size N", fontsize=11)
    ax.set_ylabel("Runtime (ms, log scale)", fontsize=11)
    ax.set_title("Classical search runtime vs database size\n(worst case — target at last position)",
                 fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, which='both', alpha=0.3)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    plt.tight_layout()
    _save(fig, "chart1_classical_runtime.png")


def chart2_queries(rows):
    """Classical comparisons vs quantum queries vs N."""
    ns       = [r["N"] for r in rows]
    lin_cmp  = [r["N"] for r in rows]             # worst case = N
    q_queries= [quantum_queries(r["N"]) for r in rows]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.loglog(ns, lin_cmp,  'o-',  color=CORAL,  lw=2.5, ms=5, label='Classical O(N)')
    ax.loglog(ns, q_queries, 's--', color=PURPLE, lw=2.5, ms=5, label='Grover O(√N)')

    # Reference lines
    ns_ref = np.array(ns, dtype=float)
    ax.loglog(ns_ref, ns_ref,          ':', color=CORAL,  alpha=0.3, lw=1)
    ax.loglog(ns_ref, np.sqrt(ns_ref), ':', color=PURPLE, alpha=0.3, lw=1)

    # Annotate the N=1M point
    n_last = ns[-1]
    ax.annotate(f"N={n_last:,}\nClassical: {n_last:,}\nQuantum: {quantum_queries(n_last):,}",
                xy=(n_last, quantum_queries(n_last)),
                xytext=(n_last / 80, quantum_queries(n_last) * 20),
                fontsize=8, color=PURPLE,
                arrowprops=dict(arrowstyle='->', color=PURPLE, lw=0.8))

    ax.set_xlabel("Database size N", fontsize=11)
    ax.set_ylabel("Number of queries (log scale)", fontsize=11)
    ax.set_title("Classical O(N) vs Grover O(√N) — queries required\nQuantum advantage grows as database scales",
                 fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, which='both', alpha=0.3)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    plt.tight_layout()
    _save(fig, "chart2_queries_comparison.png")


def chart3_speedup(rows):
    """Speedup ratio (N / sqrt(N) = sqrt(N)) vs database size."""
    ns      = [r["N"] for r in rows]
    speedup = [r["speedup_ratio"] for r in rows]

    # Annotate key forensic scales
    forensic_points = {
        1_000:       "Lab DB\n1K",
        100_000:     "Regional\n100K",
        1_048_576:   "~1M records",
    }

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.semilogx(ns, speedup, 'o-', color=TEAL, lw=2.5, ms=6)
    ax.fill_between(ns, speedup, alpha=0.08, color=TEAL)

    for n_key, label in forensic_points.items():
        if n_key in ns:
            idx = ns.index(n_key)
            ax.annotate(label, xy=(n_key, speedup[idx]),
                        xytext=(n_key, speedup[idx] + 30),
                        fontsize=8, ha='center', color=TEAL,
                        arrowprops=dict(arrowstyle='->', color=TEAL, lw=0.8))

    ax.set_xlabel("Database size N", fontsize=11)
    ax.set_ylabel("Speedup factor (classical / quantum queries)", fontsize=11)
    ax.set_title("Quantum speedup ratio vs database size\nSpeedup ≈ √N — grows with every database scale-up",
                 fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    plt.tight_layout()
    _save(fig, "chart3_speedup_ratio.png")


def chart4_success_prob(rows):
    """Grover success probability vs N."""
    ns    = [r["N"] for r in rows]
    probs = [r["quantum_prob"] for r in rows]

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.semilogx(ns, probs, 'o-', color=PURPLE, lw=2, ms=5)
    ax.axhline(y=100, color=GRAY, lw=1, ls=':', label='100% ceiling')
    ax.axhline(y=90,  color=TEAL, lw=1, ls='--', label='90% threshold')
    ax.fill_between(ns, probs, 90, where=[p >= 90 for p in probs],
                    alpha=0.1, color=TEAL, label='Above 90%')

    ax.set_xlabel("Database size N", fontsize=11)
    ax.set_ylabel("Success probability (%)", fontsize=11)
    ax.set_ylim(50, 105)
    ax.set_title("Grover success probability at optimal k = ⌊π/4·√N⌋\nRemains above 90% across all forensic database sizes",
                 fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    plt.tight_layout()
    _save(fig, "chart4_success_probability.png")


if __name__ == "__main__":
    print("=" * 55)
    print("CHART GENERATOR — producing 4 comparison plots")
    print("=" * 55)

    print("\nRunning scaling test to collect data...")
    rows = run_scaling_test(verbose=False)

    print("\nGenerating charts:")
    chart1_runtime(rows)
    chart2_queries(rows)
    chart3_speedup(rows)
    chart4_success_prob(rows)

    print("\nAll 4 charts saved to results/")