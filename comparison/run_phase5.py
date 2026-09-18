# comparison/run_phase5.py
# Master Phase 5 runner — executes all comparison scripts in sequence.

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comparison.benchmark        import run_full_benchmark
from comparison.scaling_test     import run_scaling_test
from comparison.complexity_analysis import run_complexity_analysis
from comparison.charts           import (run_scaling_test as get_rows,
                                         chart1_runtime, chart2_queries,
                                         chart3_speedup, chart4_success_prob)
from comparison.report           import generate_report


def main():
    print("\n" + "=" * 68)
    print("PHASE 5 — COMPLETE CLASSICAL vs QUANTUM COMPARISON")
    print("=" * 68)

    print("\n[1/5]  Full benchmark (N=16, all methods)...")
    run_full_benchmark()

    print("\n[2/5]  Scaling test (N=8 to 1,048,576)...")
    rows = run_scaling_test()

    print("\n[3/5]  Complexity analysis (forensic scales)...")
    run_complexity_analysis()

    print("\n[4/5]  Generating 4 comparison charts...")
    chart1_runtime(rows)
    chart2_queries(rows)
    chart3_speedup(rows)
    chart4_success_prob(rows)

    print("\n[5/5]  Generating final report...")
    generate_report()

    print("\n" + "=" * 68)
    print("PHASE 5 COMPLETE")
    print("All outputs saved to results/:")
    print("  scaling_data.csv")
    print("  chart1_classical_runtime.png")
    print("  chart2_queries_comparison.png")
    print("  chart3_speedup_ratio.png")
    print("  chart4_success_probability.png")
    print("  final_report.txt")
    print("=" * 68)


if __name__ == "__main__":
    main()