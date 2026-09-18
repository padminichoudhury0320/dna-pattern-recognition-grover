# quantum/grover.py
# Builds the complete Grover circuit:
#   - State preparation (Hadamard on all qubits)
#   - Repeated (Oracle + Diffuser) for k iterations
#   - Measurement
#
# Also contains the diffuser subcircuit and iteration calculator.

import math
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from quantum.oracle import build_oracle


def build_diffuser(num_qubits: int) -> QuantumCircuit:
    """
    Build the Grover diffusion operator (inversion about the mean).

    The diffuser is the same circuit regardless of which target is marked.
    It reflects all amplitudes around their average, amplifying the
    phase-flipped (target) state and suppressing all others.

    Circuit structure:
        H⊗n → X⊗n → H(last) → MCX → H(last) → X⊗n → H⊗n

    This implements: D = H⊗n (2|0⟩⟨0| − I) H⊗n = 2|s⟩⟨s| − I
    where |s⟩ is the uniform superposition.
    """
    qr       = QuantumRegister(num_qubits, name='q')
    diffuser = QuantumCircuit(qr, name='Diffuser')

    # Step 1: H on all qubits — rotate to computational basis
    diffuser.h(qr)

    # Step 2: X on all qubits — flip so |0...0⟩ becomes the marked state
    diffuser.x(qr)

    # Step 3: Multi-controlled Z on |1...1⟩ (which was |0...0⟩ before X)
    diffuser.h(qr[-1])
    diffuser.mcx(list(range(num_qubits - 1)), num_qubits - 1)
    diffuser.h(qr[-1])

    # Step 4: Undo X
    diffuser.x(qr)

    # Step 5: H on all qubits — rotate back to superposition basis
    diffuser.h(qr)

    return diffuser


def optimal_iterations(num_items: int) -> int:
    """
    Calculate the optimal number of Grover iterations.
    Formula: k = floor( (π/4) · √N )

    Running more than k iterations decreases success probability.
    Running fewer leaves probability lower than maximum.
    """
    return max(1, math.floor((math.pi / 4) * math.sqrt(num_items)))


def build_grover_circuit(target_index: int,
                          num_qubits: int,
                          num_items: int,
                          iterations: int = None) -> QuantumCircuit:
    """
    Build the complete Grover search circuit.

    Args:
        target_index : integer index of the target DNA record
        num_qubits   : number of qubits (ceil(log2(num_items)))
        num_items    : total number of database records (N)
        iterations   : Grover iterations (default: optimal = floor(π/4 · √N))

    Returns:
        Full QuantumCircuit ready to simulate, with measurement.

    Circuit layout:
        [H⊗n] → [Oracle + Diffuser] × k → [Measure]
    """
    if iterations is None:
        iterations = optimal_iterations(num_items)

    qr = QuantumRegister(num_qubits, name='q')
    cr = ClassicalRegister(num_qubits, name='c')
    qc = QuantumCircuit(qr, cr)

    # ── Stage 1: Equal superposition of all N states ──────────────────────
    # H applied to every qubit puts the system into:
    # |s⟩ = (1/√N) · (|0⟩ + |1⟩ + ... + |N-1⟩)
    qc.h(qr)
    qc.barrier()

    # ── Stage 2: Grover iterations ────────────────────────────────────────
    oracle   = build_oracle(target_index, num_qubits)
    diffuser = build_diffuser(num_qubits)

    for i in range(iterations):
        # Oracle: flip phase of target state
        qc.append(oracle,   qr)
        qc.barrier()
        # Diffuser: amplify target amplitude
        qc.append(diffuser, qr)
        qc.barrier()

    # ── Stage 3: Measure all qubits ───────────────────────────────────────
    qc.measure(qr, cr)

    return qc


# ── Self-test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database    import build_database, get_target
    from dna_encoder import get_num_qubits

    db         = build_database()
    target     = get_target()
    num_qubits = get_num_qubits(len(db))
    num_items  = len(db)

    target_idx = next(i for i, r in enumerate(db)
                      if r["sequence"] == target["sequence"])

    k = optimal_iterations(num_items)

    print("=" * 55)
    print("GROVER CIRCUIT — SELF TEST")
    print("=" * 55)
    print(f"\nDatabase size    : {num_items} records")
    print(f"Qubits           : {num_qubits}")
    print(f"Target           : {target['sequence']}  (index {target_idx})")
    print(f"Optimal iters k  : {k}  [floor(π/4 · √{num_items})]")

    # Build and inspect the diffuser alone
    diff = build_diffuser(num_qubits)
    print(f"\nDiffuser circuit  ({diff.size()} gates, depth {diff.depth()}):")
    print(diff.draw(output='text'))

    # Build the full Grover circuit
    grover_qc = build_grover_circuit(target_idx, num_qubits, num_items)

    print(f"\nFull Grover circuit ({grover_qc.size()} gates, depth {grover_qc.depth()}):")
    print(grover_qc.draw(output='text', fold=120))

    print("\nCircuit summary:")
    print(f"  Qubits         : {grover_qc.num_qubits}")
    print(f"  Classical bits : {grover_qc.num_clbits}")
    print(f"  Total gates    : {grover_qc.size()}")
    print(f"  Circuit depth  : {grover_qc.depth()}")
    print(f"  Iterations     : {k}")
    print(f"\nCircuit is ready for simulation in Phase 4.")
    
