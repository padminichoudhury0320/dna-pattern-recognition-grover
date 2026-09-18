# quantum/oracle.py
# Builds the Grover oracle for a given target DNA index.
# The oracle marks the target state by flipping its phase.
# Everything else is unchanged.

from qiskit import QuantumCircuit, QuantumRegister

def build_oracle(target_index: int, num_qubits: int) -> QuantumCircuit:
    """
    Build the phase-flip oracle for Grover's algorithm.

    Args:
        target_index : integer index of the target DNA record (0 to N-1)
        num_qubits   : number of qubits = ceil(log2(N))

    Returns:
        A QuantumCircuit that flips the phase of |target_index⟩ only.

    How it works:
        1. Convert target_index to binary string (the bit pattern to mark).
        2. For every bit that is 0, apply X gate before AND after the MCZ.
           This turns "control on |0⟩" into "control on |1⟩".
        3. Apply a multi-controlled Z (decomposed as H·MCX·H on last qubit).
        4. The combined effect: phase of |target_index⟩ flips from + to −.
    """
    qr     = QuantumRegister(num_qubits, name='q')
    oracle = QuantumCircuit(qr, name='Oracle')

    # Convert target index to binary, padded to num_qubits bits
    # e.g. index 9 with 4 qubits → '1001'
    target_bits = format(
        target_index,
        f'0{num_qubits}b'
    )[::-1]

    # Step 1: X gates on qubits where target bit is 0
    zero_positions = [i for i, bit in enumerate(target_bits) if bit == '0']
    for pos in zero_positions:
        oracle.x(qr[pos])

    # Step 2: Multi-controlled Z via H · MCX · H on the last qubit
    # This flips phase only when all control qubits are |1⟩
    oracle.h(qr[-1])                                       # H on target qubit
    oracle.mcx(list(range(num_qubits - 1)), num_qubits - 1)  # MCX (Toffoli generalised)
    oracle.h(qr[-1])                                       # H restores

    # Step 3: Undo the X gates (restore qubit states)
    for pos in zero_positions:
        oracle.x(qr[pos])

    return oracle


def get_oracle_explanation(target_index: int, num_qubits: int) -> str:
    """
    Return a human-readable explanation of what the oracle does
    for a specific target, useful for debugging and reporting.
    """
    target_bits = format(target_index, f'0{num_qubits}b')
    zero_pos    = [i for i, b in enumerate(target_bits) if b == '0']
    one_pos     = [i for i, b in enumerate(target_bits) if b == '1']

    lines = [
        f"Oracle target  : index {target_index} → |{target_bits}⟩",
        f"Qubits with 1  : {one_pos} — controlled directly (no X wrap needed)",
        f"Qubits with 0  : {zero_pos} — wrapped with X gates to make them 1-controls",
        f"Phase flip     : only |{target_bits}⟩ gets phase −1, all others unchanged",
    ]
    return "\n".join(lines)


# ── Self-test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database import build_database, get_target
    from dna_encoder import get_num_qubits

    db         = build_database()
    target     = get_target()
    num_qubits = get_num_qubits(len(db))    # = 4 for 16 records

    print("=" * 55)
    print("ORACLE CONSTRUCTION — SELF TEST")
    print("=" * 55)

    # Find the index of GTAC in our ordered database
    target_idx = next(i for i, r in enumerate(db) if r["sequence"] == target["sequence"])

    print(f"\nDatabase size  : {len(db)} records")
    print(f"Qubits needed  : {num_qubits}")
    print(f"Target sequence: {target['sequence']}")
    print(f"Target index   : {target_idx}")
    print()
    print(get_oracle_explanation(target_idx, num_qubits))

    oracle = build_oracle(target_idx, num_qubits)

    print("\nOracle circuit:")
    print(oracle.draw(output='text'))

    print(f"\nOracle gate count : {oracle.size()} gates")
    print(f"Oracle depth      : {oracle.depth()} layers")