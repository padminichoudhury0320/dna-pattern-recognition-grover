# quantum/iteration_analysis.py
# Prints a table showing target probability at each iteration count.
# Demonstrates WHY we need exactly k = floor(π/4 · √N) iterations.

import math, sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database        import build_database, get_target
from dna_encoder     import get_num_qubits
from quantum.grover  import build_grover_circuit, optimal_iterations
from quantum.simulator import run_statevector

db          = build_database()
target      = get_target()
num_qubits  = get_num_qubits(len(db))
num_items   = len(db)
target_idx  = next(i for i, r in enumerate(db) if r["sequence"] == target["sequence"])
target_bits = format(target_idx, f'0{num_qubits}b')
k_opt       = optimal_iterations(num_items)

print("=" * 60)
print(f"ITERATION ANALYSIS  |  N={num_items}  |  k_optimal={k_opt}")
print(f"Target: {target['sequence']}  →  |{target_bits}⟩  (index {target_idx})")
print("=" * 60)
print(f"\n{'Iters':>6}  {'P(target)':>10}  {'Bar':30}  Note")
print("-" * 60)

for iters in range(0, k_opt * 3 + 1):
    if iters == 0:
        prob = 1.0 / num_items
    else:
        qc   = build_grover_circuit(target_idx, num_qubits, num_items, iterations=iters)
        sv   = run_statevector(qc, num_qubits)
        prob = sv["probabilities"].get(target_bits, 0.0)

    bar  = "█" * int(prob * 30)
    note = ""
    if iters == 0:      note = "← uniform superposition"
    if iters == k_opt:  note = "← OPTIMAL ✓"
    if prob < 1/num_items and iters > 0:
        note = "← below classical baseline!"

    print(f"{iters:>6}  {prob:>10.4f}  {bar:30}  {note}\n")