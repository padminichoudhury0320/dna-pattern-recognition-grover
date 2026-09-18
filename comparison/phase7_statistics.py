# comparison/phase7_statistics.py

"""
Phase 7 - Statistical Benchmarking

Runs:

1. Linear Search
2. KMP Search
3. Rabin-Karp Search

Across database sizes:

16
32
64
128
256

For each size:
- Random target selected
- Multiple trials
- Average runtime
- Average comparisons
- Success rate

Outputs:

results/phase7_statistics.csv
"""

import os
import sys
import json
import csv
import random

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from classical.linear_search import linear_search
from classical.kmp_search import kmp_search
from classical.rabin_karp import rabin_karp_search


RESULTS_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    "results"
)

TRIALS = 100

DATABASE_SIZES = [
    16,
    32,
    64,
    128,
    256
]


def load_database(size):
    """
    Load scaled database JSON.
    """

    filename = os.path.join(
        RESULTS_DIR,
        f"scaled_db_{size}.json"
    )

    with open(filename, "r") as f:
        return json.load(f)


def evaluate_algorithm(
    algorithm,
    database,
    trials=TRIALS
):
    """
    Run repeated random-target tests.
    """

    total_time = 0.0
    total_comparisons = 0
    successes = 0

    for _ in range(trials):

        target_record = random.choice(database)

        target_sequence = (
            target_record["sequence"]
        )

        result = algorithm(
            database,
            target_sequence
        )

        total_time += result["time_ms"]
        total_comparisons += result["comparisons"]

        if result["found"] is not None:
            successes += 1

    return {
        "avg_time_ms":
            total_time / trials,

        "avg_comparisons":
            total_comparisons / trials,

        "success_rate":
            successes / trials
    }


def main():

    print("=" * 60)
    print("PHASE 7 STATISTICAL BENCHMARK")
    print("=" * 60)

    rows = []

    algorithms = [
        ("Linear", linear_search),
        ("KMP", kmp_search),
        ("Rabin-Karp", rabin_karp_search)
    ]

    for size in DATABASE_SIZES:

        print(f"\nDatabase Size = {size}")

        db = load_database(size)

        for name, func in algorithms:

            print(
                f"  Running {name}..."
            )

            stats = evaluate_algorithm(
                func,
                db
            )

            rows.append({
                "database_size": size,
                "algorithm": name,
                "avg_time_ms":
                    round(
                        stats["avg_time_ms"],
                        6
                    ),

                "avg_comparisons":
                    round(
                        stats["avg_comparisons"],
                        2
                    ),

                "success_rate":
                    round(
                        stats["success_rate"],
                        4
                    )
            })

            print(
                f"    Time: "
                f"{stats['avg_time_ms']:.6f} ms"
            )

            print(
                f"    Comparisons: "
                f"{stats['avg_comparisons']:.2f}"
            )

    output_file = os.path.join(
        RESULTS_DIR,
        "phase7_statistics.csv"
    )

    with open(
        output_file,
        "w",
        newline=""
    ) as csvfile:

        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "database_size",
                "algorithm",
                "avg_time_ms",
                "avg_comparisons",
                "success_rate"
            ]
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    print("\n")
    print("=" * 60)
    print("Benchmark Complete")
    print("=" * 60)

    print(
        f"Saved:\n{output_file}"
    )


if __name__ == "__main__":
    main()