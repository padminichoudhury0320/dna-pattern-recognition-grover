# verify_phase1.py
from dna_encoder import encode_sequence, decode_sequence, get_num_qubits
from database import build_database, get_target
from utils import print_section, display_binary_table

print_section("PHASE 1 VERIFICATION")

db = build_database()
target = get_target()

print(f"\nDatabase size     : {len(db)} sequences")
print(f"Sequence length   : 4 bases = 8 bits per record")
print(f"Qubits required   : {get_num_qubits(len(db))}")
print(f"Crime scene sample: {target['sequence']}  ->  binary: {target['binary']}  ->  index: {target['int_index']}")

print("\nFull encoded database:")
display_binary_table(db)

# Confirm target exists in database
match = next((r for r in db if r["sequence"] == target["sequence"]), None)
print(f"\nTarget in database: {'YES — ' + match['name'] if match else 'NO'}")
print("\nPhase 1 complete. Ready for Phase 2 (Classical Search).")