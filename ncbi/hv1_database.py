# ncbi/hv1_database.py  — FINAL VERSION
# Problem solved: previous batches came from single population studies,
# producing similar HV1 windows. Fix: search across multiple population-associated terms
# and merge results to increase sequence diversity in the retrieved set.

import time, os, sys, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Bio import Entrez, SeqIO
from ncbi.hv1_encoder import DEFAULT_WINDOW_SIZE

WINDOW_SIZE = DEFAULT_WINDOW_SIZE

Entrez.email = os.getenv("NCBI_EMAIL", "your_email@example.com")

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
CACHE_FILE  = os.path.join(RESULTS_DIR, "hv1_ncbi_cache.json")
os.makedirs(RESULTS_DIR, exist_ok=True)

TARGET_RECORDS = 16

# Window start offset within HV1 — shift by 10 bases to hit
# the most variable part of HV1 (positions ~16035-16043 are
# highly polymorphic across populations)
HV1_WINDOW_OFFSET = 10   # skip first 10 bases, use bases 10-17

# Search multiple population-associated queries to increase diversity in the retrieved set.
# Each query targets records associated with a different geographic or population-related term.
# The resulting records are deduplicated by accession and extracted sequence; individual-level independence is not independently verified by this script.
POPULATION_QUERIES = [
    'Homo sapiens[Organism] AND mitochondrion[Title] AND "complete genome"[Title] AND 16000:17000[SLEN] AND African[All Fields]',
    'Homo sapiens[Organism] AND mitochondrion[Title] AND "complete genome"[Title] AND 16000:17000[SLEN] AND European[All Fields]',
    'Homo sapiens[Organism] AND mitochondrion[Title] AND "complete genome"[Title] AND 16000:17000[SLEN] AND Asian[All Fields]',
    'Homo sapiens[Organism] AND mitochondrion[Title] AND "complete genome"[Title] AND 16000:17000[SLEN] AND Indian[All Fields]',
    'Homo sapiens[Organism] AND mitochondrion[Title] AND "complete genome"[Title] AND 16000:17000[SLEN] AND haplogroup[All Fields]',
    'Homo sapiens[Organism] AND mitochondrion[Title] AND "complete genome"[Title] AND 16000:17000[SLEN] AND forensic[All Fields]',
]


def search_population(query: str, n: int = 8) -> list:
    """Search NCBI with one population query, return NCBI internal IDs."""
    try:
        handle = Entrez.esearch(
            db="nucleotide", term=query,
            retmax=n, sort="relevance"
        )
        record = Entrez.read(handle)
        handle.close()
        time.sleep(0.34)
        return record["IdList"]
    except Exception as e:
        print(f"    Search failed: {e}")
        return []


def fetch_one(ncbi_id: str, offset: int = HV1_WINDOW_OFFSET) -> dict:
    """
    Fetch one complete mitochondrial genome and extract HV1 window.
    Uses offset to hit the most variable part of HV1.
    """
    from ncbi.hv1_encoder import HV1_START, HV1_END, encode_window, encode_to_index

    handle = Entrez.efetch(
        db="nucleotide", id=ncbi_id,
        rettype="gb", retmode="text"
    )
    record = SeqIO.read(handle, "genbank")
    handle.close()

    if len(record.seq) < 16400:
        raise ValueError(f"Too short: {len(record.seq)} bp")

    # Extract HV1 region
    seq  = str(record.seq).upper()
    hv1  = seq[HV1_START:HV1_END]
    # Clean: keep only ATGC
    clean_hv1 = ''.join(b for b in hv1 if b in 'ATGC')

    if len(clean_hv1) < offset + WINDOW_SIZE:
        raise ValueError(f"HV1 too short after cleaning: {len(clean_hv1)} bases")

    window = clean_hv1[offset: offset + WINDOW_SIZE]
    binary = encode_window(window)
    index  = encode_to_index(window)

    return {
        "id":          record.id,
        "name":        record.name,
        "description": record.description[:60],
        "sequence":    window,
        "binary":      binary,
        "int_index":   index,
        "hv1_preview": clean_hv1[:20] + "...",
        "source":      "NCBI GenBank",
        "full_length": len(record.seq),
    }


def build_hv1_database(use_cache: bool = True) -> list:
    """
    Build HV1 database from multiple population searches.
    Guarantees diversity by pulling from 6 different population queries.
    """
    if use_cache and os.path.exists(CACHE_FILE):
        print(f"Loading from cache: {CACHE_FILE}")
        with open(CACHE_FILE) as f:
            db = json.load(f)
        print(f"Loaded {len(db)} records from cache.")
        return db

    print(f"Searching across {len(POPULATION_QUERIES)} population groups...")
    print(f"(Targets {TARGET_RECORDS} unique records)\n")

    # Collect candidate IDs from all population queries
    all_ids = []
    seen_ids = set()
    for i, query in enumerate(POPULATION_QUERIES, 1):
        label = query.split("AND")[-1].strip()[:30]
        print(f"  Query {i}/{len(POPULATION_QUERIES)}: {label}")
        ids = search_population(query, n=8)
        new_ids = [id_ for id_ in ids if id_ not in seen_ids]
        seen_ids.update(new_ids)
        all_ids.extend(new_ids)
        print(f"    Found {len(ids)} — {len(new_ids)} new unique IDs")

    print(f"\nTotal unique candidate IDs: {len(all_ids)}")
    print(f"Fetching sequences...\n")

    db        = []
    seen_wins = set()
    fetched   = 0

    for ncbi_id in all_ids:
        if len(db) >= TARGET_RECORDS:
            break
        fetched += 1
        try:
            print(f"  [{fetched:02d}] ID {ncbi_id}...", end=" ")
            rec = fetch_one(ncbi_id)

            if rec["sequence"] in seen_wins:
                print(f"duplicate ({rec['sequence']}) — skipped")
                time.sleep(0.34)
                continue

            seen_wins.add(rec["sequence"])
            db.append(rec)
            print(f"OK  {rec['id']:<16} len={rec['full_length']}bp  "
                  f"window={rec['sequence']}  idx={rec['int_index']}")
            time.sleep(0.34)

        except Exception as e:
            print(f"FAILED — {e}")
            time.sleep(0.34)

    # If still under target, fall back to a broad search
    if len(db) < TARGET_RECORDS:
        print(f"\nOnly {len(db)} records so far. Running broad fallback search...")
        fallback_q = (
            'Homo sapiens[Organism] AND mitochondrion[Title] '
            'AND "complete genome"[Title] AND 16000:17000[SLEN]'
        )
        handle = Entrez.esearch(
            db="nucleotide", term=fallback_q,
            retmax=200, sort="relevance"
        )
        record_e = Entrez.read(handle)
        handle.close()

        for ncbi_id in record_e["IdList"]:
            if len(db) >= TARGET_RECORDS:
                break
            if ncbi_id in seen_ids:
                continue
            seen_ids.add(ncbi_id)
            fetched += 1
            try:
                print(f"  [F{fetched:02d}] ID {ncbi_id}...", end=" ")
                rec = fetch_one(ncbi_id)
                if rec["sequence"] in seen_wins:
                    print(f"duplicate ({rec['sequence']}) — skipped")
                    time.sleep(0.34)
                    continue
                seen_wins.add(rec["sequence"])
                db.append(rec)
                print(f"OK  {rec['id']:<16} window={rec['sequence']}")
                time.sleep(0.34)
            except Exception as e:
                print(f"FAILED — {e}")
                time.sleep(0.34)

    print(f"\nDatabase built: {len(db)} unique records")

    with open(CACHE_FILE, "w") as f:
        json.dump(db, f, indent=2)
    print(f"Cached: {CACHE_FILE}")

    return db


def get_hv1_target(db: list) -> dict:
    """Return the first record as the crime scene target."""
    return {
        "sequence":  db[0]["sequence"],
        "binary":    db[0]["binary"],
        "int_index": db[0]["int_index"],
        "source":    "Crime scene HV1 sample",
    }


if __name__ == "__main__":
    print("=" * 65)
    print("HV1 NCBI DATABASE — MULTI-POPULATION BUILD")
    print("=" * 65)

    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        print("Deleted old cache.\n")

    db     = build_hv1_database(use_cache=False)
    target = get_hv1_target(db)

    print(f"\n{'Accession':<16} {'Length':>7}  {'Window':<12} {'Index':>7}")
    print("-" * 50)
    for rec in db:
        mark = " ← TARGET" if rec["sequence"] == target["sequence"] else ""
        print(f"{rec['id']:<16} {rec['full_length']:>7}  "
              f"{rec['sequence']:<12} {rec['int_index']:>7}{mark}")

    print(f"\nTotal records : {len(db)}")
    print(f"Window size   : {WINDOW_SIZE} bases = {WINDOW_SIZE*2} bits")
    print(f"Target        : {target['sequence']}  binary: {target['binary']}")
