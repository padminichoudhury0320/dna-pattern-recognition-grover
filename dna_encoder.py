# dna_encoder.py
# Converts DNA sequences (A, T, G, C) into binary strings for both
# classical processing and quantum circuit loading.

BASE_TO_BITS = {
    'A': '00',
    'T': '01',
    'G': '10',
    'C': '11'
}

BITS_TO_BASE = {v: k for k, v in BASE_TO_BITS.items()}  # reverse map


def encode_sequence(sequence: str) -> str:
    """
    Convert a DNA sequence string into a binary string.
    Example: 'ATGC' -> '00011011'
    """
    sequence = sequence.upper().strip()
    _validate_sequence(sequence)
    return ''.join(BASE_TO_BITS[base] for base in sequence)


def decode_sequence(binary: str) -> str:
    """
    Convert a binary string back into a DNA sequence.
    Example: '00011011' -> 'ATGC'
    """
    if len(binary) % 2 != 0:
        raise ValueError(f"Binary string length must be even, got {len(binary)}")
    return ''.join(BITS_TO_BASE[binary[i:i+2]] for i in range(0, len(binary), 2))


def encode_to_int(sequence: str) -> int:
    """
    Convert a DNA sequence to an integer index.
    Used to identify which quantum state corresponds to which sequence.
    Example: 'AT' -> binary '0001' -> integer 1
    """
    return int(encode_sequence(sequence), 2)


def _validate_sequence(sequence: str):
    """Raise an error if the sequence contains invalid bases."""
    valid = set(BASE_TO_BITS.keys())
    invalid = set(sequence) - valid
    if invalid:
        raise ValueError(f"Invalid bases found: {invalid}. Only A, T, G, C allowed.")


def get_num_qubits(num_sequences: int) -> int:
    """
    Calculate how many qubits are needed to represent a database
    of a given size. Needs ceil(log2(N)) qubits.
    """
    import math
    return math.ceil(math.log2(num_sequences))


# ----- Quick self-test (runs when you execute this file directly) -----
if __name__ == "__main__":
    test_cases = [
        ("A",    "00"),
        ("T",    "01"),
        ("G",    "10"),
        ("C",    "11"),
        ("AT",   "0001"),
        ("ATGC", "00011011"),
        ("GGAT", "10100001"),
    ]

    print("=" * 50)
    print("DNA ENCODER — SELF TEST")
    print("=" * 50)

    all_passed = True
    for seq, expected_bin in test_cases:
        encoded = encode_sequence(seq)
        decoded = decode_sequence(encoded)
        status = "PASS" if encoded == expected_bin and decoded == seq else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"[{status}]  {seq!r:8} -> {encoded!r:18} -> decoded: {decoded!r}")

    print()
    print("Round-trip test (encode then decode must return original):", 
          "ALL PASSED" if all_passed else "SOME FAILED")

    print()
    print("Integer index examples:")
    for seq in ["AA", "AT", "AG", "AC"]:
        print(f"  encode_to_int({seq!r}) = {encode_to_int(seq)}")

    print()
    print("Qubit requirements:")
    for n in [4, 8, 16, 64, 256]:
        print(f"  {n} sequences needs {get_num_qubits(n)} qubits")