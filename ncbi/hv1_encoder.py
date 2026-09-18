# ncbi/hv1_encoder.py
# Encodes real mitochondrial HV1 sequences into binary for quantum processing.
#
# The HV1 (Hypervariable Region 1) sits at positions 16024–16365
# in the human mitochondrial genome (rCRS reference).
#
# Encoding strategy:
#   - Extract a fixed-length window from HV1
#   - Encode each base:
#
#         A = 00
#         T = 01
#         G = 10
#         C = 11
#
#   - Result: binary string of length 2W bits
#
# Example:
#
#     ATGC
#
#     A = 00
#     T = 01
#     G = 10
#     C = 11
#
#     Binary = 00011011
#
# Why use only a window?
#
# Full HV1:
#     342 bases
#     684 bits
#     ~684 qubits
#
# Classical quantum simulators cannot handle this scale.
#
# Therefore:
#
#     Real HV1 region
#           ↓
#     Small forensic window
#           ↓
#     Grover demonstration
#           ↓
#     Mathematical extrapolation
#
# This project uses a small window to keep the demonstration
# computationally tractable on a classical quantum simulator.

BASE_TO_BITS = {
    "A": "00",
    "T": "01",
    "G": "10",
    "C": "11"
}

BITS_TO_BASE = {v: k for k, v in BASE_TO_BITS.items()}

# ------------------------------------------------------------------
# HV1 Coordinates
#
# Forensic literature commonly defines HV1 as:
#
#     16024 – 16365
#
# These are biological (1-based) coordinates.
#
# Python uses 0-based indexing.
#
# Therefore:
#
#     Position 16024 -> index 16023
#     Position 16365 -> slice end 16365
#
# Result:
#
#     seq[16023:16365]
#
# gives exactly 342 bases corresponding to
# positions 16024 through 16365 inclusive.
# ------------------------------------------------------------------

HV1_START = 16023
HV1_END = 16365

# Default demonstration window
DEFAULT_WINDOW_SIZE = 8


def extract_hv1(full_sequence: str) -> str:
    """
    Extract the HV1 region from a complete mitochondrial genome.

    Parameters
    ----------
    full_sequence : str
        Complete mtDNA genome sequence.

    Returns
    -------
    str
        HV1 region.
    """

    seq = str(full_sequence).upper()

    if len(seq) < HV1_END:
        raise ValueError(
            f"Sequence too short ({len(seq)} bp). "
            f"Expected complete mitochondrial genome "
            f"containing HV1 coordinates."
        )

    hv1 = seq[HV1_START:HV1_END]

    ambiguous = [
        base for base in hv1
        if base not in BASE_TO_BITS
    ]

    if ambiguous:
        raise ValueError(
            "HV1 contains ambiguous bases "
            f"(example: {ambiguous[:5]})."
        )

    return hv1


def extract_window(
        full_sequence: str,
        window: int = DEFAULT_WINDOW_SIZE,
        offset: int = 0
) -> str:
    """
    Extract a window from the HV1 region.

    Example
    -------
    offset = 0
        first window

    offset = 50
        starts 50 bases into HV1

    window = 8
        extracts 8 bases
    """

    hv1 = extract_hv1(full_sequence)

    if len(hv1) < offset + window:
        raise ValueError(
            f"HV1 too short: need {offset + window} bases "
            f"but only {len(hv1)} available"
        )

    return hv1[offset:offset + window]


def encode_window(sequence_window: str) -> str:
    """
    Encode DNA window into binary.

    Example
    -------
    ATGC -> 00011011
    """

    sequence_window = sequence_window.upper()

    invalid = set(sequence_window) - set(BASE_TO_BITS)

    if invalid:
        raise ValueError(
            f"Invalid DNA bases: {invalid}"
        )

    return ''.join(
        BASE_TO_BITS[base]
        for base in sequence_window
    )


def decode_binary(binary: str) -> str:
    """
    Decode binary back to DNA sequence.

    Example
    -------
    00011011 -> ATGC
    """

    if len(binary) % 2 != 0:
        raise ValueError(
            "Binary length must be even."
        )

    try:
        return ''.join(
            BITS_TO_BASE[binary[i:i + 2]]
            for i in range(0, len(binary), 2)
        )

    except KeyError:
        raise ValueError(
            "Binary contains invalid DNA encoding."
        )       


def encode_to_index(sequence_window: str) -> int:
    """
    Convert DNA window to integer state index.

    Example
    -------
    ATGC

    Binary:
        00011011

    Integer:
        27
    """

    return int(
        encode_window(sequence_window),
        2
    )


def full_pipeline(
        full_sequence: str,
        window: int = DEFAULT_WINDOW_SIZE,
        offset: int = 0
) -> dict:
    """
    Complete mtDNA -> HV1 -> Binary pipeline.
    """

    hv1 = extract_hv1(full_sequence)

    selected_window = extract_window(
        full_sequence,
        window,
        offset
    )

    binary = encode_window(selected_window)

    index = encode_to_index(selected_window)

    return {
        "hv1_start": 16024,
        "hv1_end": 16365,
        "hv1_length": len(hv1),

        "hv1_preview":
            hv1[:20] + "...",

        "window": selected_window,

        "window_size":
            len(selected_window),

        "offset":
            offset,

        "binary":
            binary,

        "num_bits":
            len(binary),

        "qubits_needed":
            len(binary),

        "state_space":
            f"2^{len(binary)}",

        "int_index":
            index
    }


# ------------------------------------------------------------------
# Self Test
# ------------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("HV1 ENCODER — SELF TEST")
    print("=" * 60)

    test_cases = [
        ("AAAA", "00000000", 0),
        ("TTTT", "01010101", 85),
        ("GGGG", "10101010", 170),
        ("CCCC", "11111111", 255),
        ("ATGC", "00011011", 27),
        ("GATC", "10000111", 135),
    ]

    print(
        f"\n{'Window':<10}"
        f"{'Expected Binary':<20}"
        f"{'Got Binary':<20}"
        f"{'Index':>8}"
        f"  Status"
    )

    print("-" * 75)

    all_pass = True

    for window, expected_bin, expected_idx in test_cases:

        got_bin = encode_window(window)
        got_idx = encode_to_index(window)
        decoded = decode_binary(got_bin)

        passed = (
            got_bin == expected_bin
            and got_idx == expected_idx
            and decoded == window
        )

        if not passed:
            all_pass = False

        print(
            f"{window:<10}"
            f"{expected_bin:<20}"
            f"{got_bin:<20}"
            f"{got_idx:>8}"
            f"  {'PASS' if passed else 'FAIL'}"
        )

    print(
        f"\nOverall Result: "
        f"{'PASSED' if all_pass else 'FAILED'}"
    )

    print("\nHV1 Configuration")
    print("-" * 30)

    print(f"HV1 Start Position : 16024")
    print(f"HV1 End Position   : 16365")
    print(f"HV1 Length         : {HV1_END - HV1_START} bases")

    print(
        f"Default Window     : "
        f"{DEFAULT_WINDOW_SIZE} bases"
    )

    print(
        f"Bits Required      : "
        f"{DEFAULT_WINDOW_SIZE * 2}"
    )

    print(
        f"Addressable States : "
        f"2^{DEFAULT_WINDOW_SIZE * 2}"
    )

    print(
        f"Qubits Needed      : "
        f"{DEFAULT_WINDOW_SIZE * 2}"
    )

    print("\nWindow Extraction Test")
    print("-" * 30)

    fake_hv1 = "ATGCGTAC" * 50

    fake_mt = (
        "A" * HV1_START
        + fake_hv1
        + "A" * 5000
    )

    test_window = extract_window(
        fake_mt,
        window=8,
        offset=10
    )

    print("Extracted Window:", test_window)

    print("\nAll tests completed.")