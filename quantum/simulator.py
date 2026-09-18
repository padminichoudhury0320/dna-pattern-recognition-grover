# quantum/simulator.py
# Runs the Grover circuit on Qiskit Aer simulators.
# Two backends used:
#   1. Statevector  — exact probability amplitudes, no sampling noise
#   2. QASM         — shot-based sampling, mimics real quantum hardware
#
# Results are mapped back to DNA database records.

import math
import time
from qiskit_aer import Aer
from qiskit import transpile

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum.grover  import build_grover_circuit, optimal_iterations
from database        import build_database, get_target
from dna_encoder     import get_num_qubits


def run_statevector(grover_circuit, num_qubits: int) -> dict:
    """
    Run the Grover circuit on the statevector simulator.

    The statevector simulator computes the exact quantum state —
    no sampling, no noise. It returns the precise probability of
    every possible measurement outcome.

    Returns:
        dict mapping bitstring → probability (floats summing to 1.0)
    """
    # Remove measurement gates — statevector works on pure state
    circuit_no_measure = grover_circuit.remove_final_measurements(inplace=False)

    backend    = Aer.get_backend('statevector_simulator')
    transpiled = transpile(circuit_no_measure, backend)

    start  = time.perf_counter()
    job    = backend.run(transpiled)
    result = job.result()
    elapsed_ms = (time.perf_counter() - start) * 1000

    statevector   = result.get_statevector()
    probabilities = {}

    for i, amplitude in enumerate(statevector):
        prob = abs(amplitude) ** 2          # probability = |amplitude|²
        if prob > 1e-6:                     # ignore negligible states
            bitstring = format(i, f'0{num_qubits}b')
            probabilities[bitstring] = round(prob, 6)

    return {
        "backend":       "statevector_simulator",
        "probabilities": probabilities,
        "elapsed_ms":    elapsed_ms,
    }


def run_qasm(grover_circuit, shots: int = 1024) -> dict:
    """
    Run the Grover circuit on the QASM simulator.

    QASM sampling mimics what a real quantum computer does —
    it collapses the quantum state on each shot and records
    a classical bitstring. After many shots, the histogram of
    results reflects the underlying probability distribution.

    The most frequent bitstring = the circuit's most probable answer.

    Returns:
        dict mapping bitstring → count (integers summing to shots)
    """
    backend    = Aer.get_backend('qasm_simulator')
    transpiled = transpile(grover_circuit, backend)

    start  = time.perf_counter()
    job    = backend.run(transpiled, shots=shots)
    result = job.result()
    elapsed_ms = (time.perf_counter() - start) * 1000

    counts = result.get_counts()

    return {
        "backend":     "qasm_simulator",
        "counts":      counts,
        "shots":       shots,
        "elapsed_ms":  elapsed_ms,
    }


def map_result_to_dna(bitstring: str, database: list) -> dict:
    """
    Convert a measured bitstring back to a DNA database record.

    The bitstring is the binary index of the record in our database.
    e.g. '1001' → index 9 → Suspect_10 (GTAC)
    """
    index = int(bitstring, 2)
    if 0 <= index < len(database):
        return database[index]
    return None


def analyse_qasm_results(counts: dict, database: list, shots: int) -> list:
    """
    Sort QASM counts by frequency, map each to a DNA record,
    and compute probability as count/shots.

    Returns a sorted list of result dicts, most frequent first.
    """
    results = []
    for bitstring, count in counts.items():
        record = map_result_to_dna(bitstring, database)
        results.append({
            "bitstring":   bitstring,
            "count":       count,
            "probability": count / shots,
            "record":      record,
        })
    return sorted(results, key=lambda x: x["count"], reverse=True)


def full_grover_search(target_sequence: str = None) -> dict:
    """
    Master function: builds the Grover circuit for the target sequence,
    runs both simulators, and returns the complete structured result.

    This is the function called by the benchmark and comparison scripts.
    """
    db         = build_database()
    target     = get_target() if target_sequence is None else {
        "sequence":  target_sequence,
        "binary":    __import__('dna_encoder').encode_sequence(target_sequence),
        "int_index": __import__('dna_encoder').encode_to_int(target_sequence),
    }
    num_qubits = get_num_qubits(len(db))
    num_items  = len(db)

    # Find the integer index of the target in our ordered database
    target_idx = next(
        (i for i, r in enumerate(db) if r["sequence"] == target["sequence"]),
        None
    )
    if target_idx is None:
        raise ValueError(f"Target sequence '{target['sequence']}' not in database.")

    k = optimal_iterations(num_items)

    # Build the complete Grover circuit
    grover_qc = build_grover_circuit(target_idx, num_qubits, num_items, iterations=k)

    # Run both simulators
    sv_result   = run_statevector(grover_qc, num_qubits)
    qasm_result = run_qasm(grover_qc, shots=1024)

    # Analyse QASM results
    analysis = analyse_qasm_results(qasm_result["counts"], db, qasm_result["shots"])

    return {
        "target":        target,
        "target_idx":    target_idx,
        "num_qubits":    num_qubits,
        "num_items":     num_items,
        "iterations":    k,
        "grover_circuit": grover_qc,
        "statevector":   sv_result,
        "qasm":          qasm_result,
        "analysis":      analysis,
        "top_result":    analysis[0] if analysis else None,
    }


# ── Self-test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("QUANTUM SIMULATOR — SELF TEST")
    print("=" * 60)

    result = full_grover_search()
    target = result["target"]
    k      = result["iterations"]

    print(f"\nTarget sequence  : {target['sequence']}")
    print(f"Target index     : {result['target_idx']}")
    target_state = format(result['target_idx'], f"0{result['num_qubits']}b")
    print(f"Target state     : |{target_state}⟩")
    print(f"Grover iterations: {k}")
    print(f"Database size N  : {result['num_items']}")

    # ── Statevector results ──
    print(f"\n── Statevector simulator ({result['statevector']['elapsed_ms']:.1f} ms) ──")
    target_bits = format(result['target_idx'], f'0{result["num_qubits"]}b')
    sv_probs    = result['statevector']['probabilities']
    target_prob = sv_probs.get(target_bits, 0)

    print(f"Target |{target_bits}⟩ probability : {target_prob:.4f}  ({target_prob*100:.2f}%)")
    print(f"All other states sum           : {sum(p for k,p in sv_probs.items() if k != target_bits):.4f}")

    print("\nTop 5 states by probability:")
    top5 = sorted(sv_probs.items(), key=lambda x: x[1], reverse=True)[:5]
    for bits, prob in top5:
        record = result['analysis']
        marker = " ← TARGET" if bits == target_bits else ""
        print(f"  |{bits}⟩  {prob:.4f}  ({prob*100:.2f}%){marker}")

    # ── QASM results ──
    print(f"\n── QASM simulator — {result['qasm']['shots']} shots"
          f"  ({result['qasm']['elapsed_ms']:.1f} ms) ──")
    print(f"\n{'Rank':<5} {'Bitstring':<12} {'Count':>6} {'Prob':>8} {'Record':<14} {'Sequence'}")
    print("-" * 65)

    for rank, res in enumerate(result["analysis"][:5], 1):  
        rec  = res["record"]
        name = rec["name"] if rec else "Unknown"
        seq  = rec["sequence"] if rec else "???"
        mark = " ← MATCH" if res["bitstring"] == target_bits else ""
        print(f"{rank:<5} |{res['bitstring']}|   "
              f"{res['count']:>6} {res['probability']:>7.2%}   "
              f"{name:<14} {seq}{mark}")

    top = result["top_result"]
    print(f"\nConclusion: Top measured state = |{top['bitstring']}⟩ "
          f"→ {top['record']['name']} ({top['record']['sequence']})")
    correct = top["bitstring"] == target_bits
    print(f"Correct match: {'YES ✓' if correct else 'NO ✗'}")