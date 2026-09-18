# test_ncbi_connection.py
from Bio import Entrez, SeqIO

Entrez.email = "your_actual_email@gmail.com"  # replace with your real email

print("Testing NCBI connection...")

handle = Entrez.efetch(db="nucleotide", id="AF346980", rettype="gb", retmode="text")
record = SeqIO.read(handle, "genbank")
handle.close()

print(f"Accession : {record.id}")
print(f"Length    : {len(record.seq)} bases")
print(f"Definition: {record.description[:70]}")
print(f"First 60bp: {str(record.seq[:60])}")
print(f"\nConnection successful. NCBI access is working.")