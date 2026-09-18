# verify_phase4.py
import sys, os
sys.path.append(os.path.abspath('.'))

from quantum.simulator import full_grover_search
from database          import get_target
from dna_encoder       import get_num_qubits

print("=" * 60)
print("PHASE 4 VERIFICATION — QUANTUM SIMULATION")
print("=" * 60)

result = full_grover_search()
target = result["target"]
n_bits = result["num_qubits"]
t_bits = format(result["target_idx"], f'0{n_bits}b')

# Check 1: statevector target probability above 90%
sv_prob = result["statevector"]["probabilities"].get(t_bits, 0)
check1  = sv_prob > 0.90
print(f"\n[{'PASS' if check1 else 'FAIL'}]  Statevector target prob = {sv_prob:.4f}  (expected > 0.90)")

# Check 2: top QASM result matches target
top = result["top_result"]
check2 = top["bitstring"] == t_bits
print(f"[{'PASS' if check2 else 'FAIL'}]  Top QASM result = |{top['bitstring']}⟩  "
      f"→ {top['record']['sequence']}  (expected {target['sequence']})")

# Check 3: top result probability dominates
check3 = top["probability"] > 0.80
print(f"[{'PASS' if check3 else 'FAIL'}]  QASM top prob = {top['probability']:.2%}  (expected > 80%)")

# Check 4: correct record name
rec = top["record"]
print(f"[{'PASS' if rec else 'FAIL'}]  Mapped to database record: "
      f"{rec['name'] if rec else 'NONE'}")

print(f"\nIterations used     : {result['iterations']}  (optimal for N={result['num_items']})")
print(f"Quantum speedup     : O(√{result['num_items']}) ≈ {result['iterations']} queries")
print(f"Classical baseline  : O({result['num_items']}) = up to {result['num_items']} comparisons")

all_pass = check1 and check2 and check3 and rec
print(f"\n{'Phase 4 COMPLETE — all checks passed.' if all_pass else 'Phase 4 INCOMPLETE — fix failing checks.'}")