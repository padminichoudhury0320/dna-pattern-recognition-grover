# utils.py
# Shared display and validation helpers used across all phases.

def print_section(title: str):
    """Print a clear section header."""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_search_result(method: str, target: str, found: dict, 
                         comparisons: int, time_ms: float):
    """Standardised result display for every search method."""
    print(f"\nMethod     : {method}")
    print(f"Target     : {target}")
    if found:
        print(f"Found      : {found['name']} (ID: {found['id']})")
        print(f"Sequence   : {found['sequence']}  Binary: {found['binary']}")
    else:
        print("Found      : NO MATCH")
    print(f"Comparisons: {comparisons}")
    print(f"Time       : {time_ms:.4f} ms")


def display_binary_table(database: list):
    """Show the full database with binary encodings."""
    print(f"\n{'ID':6} {'Sequence':10} {'Binary':12} {'Dec Index':>10}")
    print("-" * 45)
    for rec in database:
        print(f"{rec['id']:6} {rec['sequence']:10} {rec['binary']:12} "
              f"{rec['int_index']:10}")