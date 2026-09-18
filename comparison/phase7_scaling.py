# comparison/phase7_scaling.py

"""
Phase 7 - Database Scaling

Purpose
-------
Create larger forensic DNA databases starting from the
real NCBI HV1 records obtained in Phase 6.

The original records remain biologically realistic.

Additional records are created through controlled
mutations of existing HV1 windows.

This allows scalability experiments for:

N = 16
N = 32
N = 64
N = 128
N = 256
"""

import random
import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from ncbi.hv1_database import build_hv1_database
from ncbi.hv1_encoder import encode_window, encode_to_index


DNA_BASES = ["A", "T", "G", "C"]


def mutate_sequence(sequence):
    """
    Create a realistic HV1 variation by mutating
    one randomly chosen position.
    """

    seq = list(sequence)

    position = random.randint(
        0,
        len(seq) - 1
    )

    original = seq[position]

    alternatives = [
        b for b in DNA_BASES
        if b != original
    ]

    seq[position] = random.choice(alternatives)

    return "".join(seq)


def create_record(sequence, index):
    """
    Create a database record compatible with
    existing project structure.
    """

    return {
        "database_index": index,
        "id": f"SYNTHETIC_{index}",
        "name": f"Synthetic HV1 Record {index}",
        "description": "Phase 7 generated record",
        "sequence": sequence,
        "binary": encode_window(sequence),
        "int_index": encode_to_index(sequence),
        "source": "NCBI-derived synthetic expansion"
    }


def expand_database(seed_db, target_size):
    """
    Expand real HV1 database to target size.
    """

    expanded = []

    seen_sequences = set()

    # Add original NCBI records first
    for i, rec in enumerate(seed_db):

        record = dict(rec)

        record["database_index"] = i

        expanded.append(record)

        seen_sequences.add(
            rec["sequence"]
        )

    next_index = len(expanded)

    while len(expanded) < target_size:

        parent = random.choice(seed_db)

        new_seq = mutate_sequence(
            parent["sequence"]
        )

        if new_seq in seen_sequences:
            continue

        seen_sequences.add(new_seq)

        expanded.append(
            create_record(
                new_seq,
                next_index
            )
        )

        next_index += 1

    return expanded


def create_scaled_database(target_size):
    """
    Create a scaled database.

    Parameters
    ----------
    target_size : int

    Returns
    -------
    list
    """

    seed_db = build_hv1_database()

    if target_size < len(seed_db):
        raise ValueError(
            f"Target size must be >= "
            f"{len(seed_db)}"
        )

    return expand_database(
        seed_db,
        target_size
    )


def generate_all_scaled_databases():
    """
    Generate all benchmark datasets.
    """

    sizes = [
        16,
        32,
        64,
        128,
        256
    ]

    datasets = {}

    for size in sizes:

        print(
            f"Generating database "
            f"N={size}"
        )

        datasets[size] = (
            create_scaled_database(size)
        )

        print(
            f"Created "
            f"{len(datasets[size])} records"
        )

    return datasets


def verify_scaled_database(db):
    """
    Basic integrity checks.
    """

    sequences = [
        rec["sequence"]
        for rec in db
    ]

    unique_count = len(
        set(sequences)
    )

    print("\nVerification")
    print("-" * 40)

    print(
        f"Total Records : {len(db)}"
    )

    print(
        f"Unique Records: {unique_count}"
    )

    print(
        "Status:",
        "PASS"
        if unique_count == len(db)
        else "FAIL"
    )


if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 7 DATABASE SCALING")
    print("=" * 60)

    datasets = (
        generate_all_scaled_databases()
    )

    largest_size = max(datasets.keys())

    largest = datasets[largest_size]

    verify_scaled_database(
        largest
    )

    print("\nExample Records\n")

    for rec in largest[:5]:
        print(
            rec["database_index"],
            rec["sequence"],
            rec["int_index"]
        )
        
        
    
import json

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

for size, db in datasets.items():

    filename = os.path.join(
        RESULTS_DIR,
        f"scaled_db_{size}.json"
    )

    with open(filename, "w") as f:
        json.dump(
            db,
            f,
            indent=2
        )

    print(
        f"Saved: {filename}"
    )