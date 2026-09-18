# database.py
# Simulated forensic DNA database — Tier 1 (controlled, hand-crafted).
# 16 sequences of length 4 bases each.
# In a real forensic context these would be STR allele combinations.

from dna_encoder import encode_sequence, encode_to_int

# Our 16 simulated suspect DNA profiles
# Each is a 4-base sequence representing one individual's marker
DNA_DATABASE = [
    {"id": "S001", "name": "Suspect_01", "sequence": "AAAA"},
    {"id": "S002", "name": "Suspect_02", "sequence": "AATG"},
    {"id": "S003", "name": "Suspect_03", "sequence": "ACGT"},
    {"id": "S004", "name": "Suspect_04", "sequence": "ATCG"},
    {"id": "S005", "name": "Suspect_05", "sequence": "TAAC"},
    {"id": "S006", "name": "Suspect_06", "sequence": "TGCA"},
    {"id": "S007", "name": "Suspect_07", "sequence": "TTGG"},
    {"id": "S008", "name": "Suspect_08", "sequence": "TCAT"},
    {"id": "S009", "name": "Suspect_09", "sequence": "GAAT"},
    {"id": "S010", "name": "Suspect_10", "sequence": "GTAC"},
    {"id": "S011", "name": "Suspect_11", "sequence": "GGCC"},
    {"id": "S012", "name": "Suspect_12", "sequence": "GCTA"},
    {"id": "S013", "name": "Suspect_13", "sequence": "CAGA"},
    {"id": "S014", "name": "Suspect_14", "sequence": "CTGA"},
    {"id": "S015", "name": "Suspect_15", "sequence": "CGAT"},
    {"id": "S016", "name": "Suspect_16", "sequence": "CCCC"},
]

# The crime scene sample — this is what we're searching for
CRIME_SCENE_SAMPLE = "GTAC"   # matches Suspect_10


def build_database():
    """
    Return the database with binary encodings and integer indices added.
    This is the processed form used by both classical and quantum search.
    """
    db = []
    for record in DNA_DATABASE:
        seq = record["sequence"]
        entry = {
            **record,
            "binary":    encode_sequence(seq),
            "int_index": encode_to_int(seq),
        }
        db.append(entry)
    return db


def get_target():
    """Return the crime scene sample with its encoding."""
    return {
        "sequence":  CRIME_SCENE_SAMPLE,
        "binary":    encode_sequence(CRIME_SCENE_SAMPLE),
        "int_index": encode_to_int(CRIME_SCENE_SAMPLE),
    }


if __name__ == "__main__":
    db = build_database()
    target = get_target()

    print("=" * 65)
    print("FORENSIC DNA DATABASE — 16 RECORDS")
    print("=" * 65)
    print(f"{'ID':6} {'Name':12} {'Sequence':10} {'Binary':10} {'Index':>6}")
    print("-" * 65)
    for rec in db:
        marker = " <-- MATCH" if rec["sequence"] == target["sequence"] else ""
        print(f"{rec['id']:6} {rec['name']:12} {rec['sequence']:10} "
              f"{rec['binary']:10} {rec['int_index']:6}{marker}")

    print()
    print("Crime scene sample:")
    print(f"  Sequence : {target['sequence']}")
    print(f"  Binary   : {target['binary']}")
    print(f"  Index    : {target['int_index']}")
    print(f"  Qubits needed for 16 records: 4")