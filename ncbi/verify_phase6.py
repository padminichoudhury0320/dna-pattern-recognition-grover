# verify_phase6.py
import sys, os, math,random
sys.path.append(os.path.abspath('.'))

from ncbi.hv1_encoder  import encode_window, decode_binary
from ncbi.hv1_database import build_hv1_database, get_hv1_target
from quantum.grover    import build_grover_circuit, optimal_iterations
from quantum.simulator import run_statevector

print("=" * 55)
print("PHASE 6 VERIFICATION")
print("=" * 55)

# Check 1: encoder round-trip
binary  = encode_window("ATGCATGC")
decoded = decode_binary(binary)
c1 = decoded == "ATGCATGC"
print(f"\n[{'PASS' if c1 else 'FAIL'}]  Encoder round-trip: "
      f"ATGCATGC → {binary} → {decoded}")

# Check 2: database size
db     = build_hv1_database(use_cache=True)
target_record = random.choice(db)

target = {
    "sequence": target_record["sequence"],
    "binary": target_record["binary"],
    "int_index": target_record["int_index"]
}
target_idx = db.index(target_record)
c2 = len(db) >= 8
print(f"[{'PASS' if c2 else 'FAIL'}]  Database size: {len(db)} records "
      f"(expected ≥ 8)")

# Check 3: required fields
required = {"id", "name", "sequence", "binary", "int_index", "source"}
c3 = all(required.issubset(r.keys()) for r in db)
print(f"[{'PASS' if c3 else 'FAIL'}]  All records have required fields")

# Check 4: target in database
c4 = any(r["sequence"] == target["sequence"] for r in db)
print(f"[{'PASS' if c4 else 'FAIL'}]  Target in database: {target['sequence']}")

# Check 5: binary lengths correct (8-base window = 16-bit binary)
c5 = all(len(r["binary"]) == len(r["sequence"]) * 2 for r in db)
print(f"[{'PASS' if c5 else 'FAIL'}]  All binary encodings correct length "
      f"({len(db[0]['sequence'])*2} bits)")

# Check 6: all from NCBI
c6 = all(r["source"] == "NCBI GenBank" for r in db)
print(f"[{'PASS' if c6 else 'FAIL'}]  All records from NCBI GenBank")

# Check 7: quantum circuit builds correctly
N          = len(db)
num_qubits = math.ceil(math.log2(N))
k          = optimal_iterations(N)
target_idx = next(i for i, r in enumerate(db)
                  if r["sequence"] == target["sequence"])
target_bits = format(target_idx, f'0{num_qubits}b')

try:
    qc = build_grover_circuit(
        target_idx,
        num_qubits,
        N,
        iterations=k
    )

    sv = run_statevector(qc, num_qubits)

    print("\nTop probabilities:")

    top_states = sorted(
        sv["probabilities"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    for bits, prob in top_states:
        print(f"  |{bits}>  {prob*100:.2f}%")

    sv_prob = sv["probabilities"].get(target_bits, 0)

    c7 = sv_prob > 0.90

    print(
        f"[{'PASS' if c7 else 'FAIL'}] "
        f"Quantum circuit: target probability = "
        f"{sv_prob*100:.2f}% (expected > 90%)"
    )

except Exception as e:
    c7 = False
    print(f"[FAIL] Quantum circuit error: {e}")

# Check 8: unique accessions
accessions = [r["id"] for r in db]
c8 = len(accessions) == len(set(accessions))
print(f"[{'PASS' if c8 else 'FAIL'}]  All accession IDs unique: "
      f"{len(set(accessions))} distinct records")

print(f"\nDatabase summary:")
print(f"  Records         : {len(db)}")
print(f"  Window size     : {len(db[0]['sequence'])} bases "
      f"({len(db[0]['sequence'])*2} bits per window)")
print(f"  Quantum qubits  : {num_qubits}  (addressing {N} records)")
print(f"  Grover iters k  : {k}")
print(f"  Target          : {target['sequence']}  →  index {target_idx}  "
      f"→  |{target_bits}⟩")
print(f"  Target accession: {db[target_idx]['id']}")

all_pass = c1 and c2 and c3 and c4 and c5 and c6 and c7 and c8
print(f"\n{'Phase 6 COMPLETE — all 8 checks passed ✓' if all_pass else 'Fix the failing checks above.'}")