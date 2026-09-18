# DNA Pattern Recognition Using Grover's Quantum Search Algorithm



A Qiskit-based research project demonstrating quantum search for DNA pattern identification, with comparisons against classical search algorithms and an NCBI GenBank mitochondrial HV1 dataset.



## Overview



This project explores how Grover's quantum search algorithm can be used as a search primitive for DNA-pattern identification and compares its query complexity with classical approaches.



The project contains two main experimental settings:



1\. **Controlled/synthetic DNA database** — a 16-record dataset used to validate the quantum circuit and compare classical and quantum search.

2\. **NCBI GenBank HV1 dataset** — 16 human mitochondrial DNA records retrieved from NCBI GenBank and represented using 8-base windows from the HV1 region.



The implementation uses **Qiskit and Qiskit Aer** for quantum-circuit construction and simulation.



> **Important:** This project demonstrates the algorithmic search concept. It is not a production forensic identification system, and the reported quantum speedup refers to oracle/query complexity rather than end-to-end forensic processing time.



## Key Results



For the controlled 16-record scaling experiment:



| Metric | Result |

|---|---:|

| Database size | 16 records |

| Address qubits | 4 |

| Grover iterations | 3 |

| Theoretical target success probability | 96.13% |

| Classical worst-case record checks | 16 |

| Grover oracle queries | 3 |

| Query-count ratio | 5.33× |



The **96.13% value is a theoretical Grover success probability** for the 16-item case. It should not be interpreted as experimental classification accuracy.



The current cached NCBI dataset contains 16 GenBank records that are traceable by accession ID. The records are deduplicated by accession and extracted sequence, but the project does not independently establish that all 16 represent unrelated individuals.



## Project Architecture



```text

DNA sequence

     |

     v

DNA encoding

     |

     +--------------------+

     |                    |

     v                    v

Classical search      Quantum search

     |                    |

     +----------+---------+

                |

                v

         Result comparison

                |

                v

       Scaling / visualization

````



### Quantum search



```text

Uniform superposition

        |

        v

   Oracle phase flip

        |

        v

Diffusion / amplitude amplification

        |

        v

Repeat for k iterations

        |

        v

     Measurement

```



For a 16-record database, 4 address qubits represent the 16 searchable indices.



## DNA Encoding



The project uses a simple 2-bit representation:



| Base | Bits |

| ---- | ---- |

| A    | `00` |

| T    | `01` |

| G    | `10` |

| C    | `11` |



Example:



```text

ATGC

 ↓

00 01 10 11

 ↓

00011011

```



The DNA sequence encoding is separate from the **database-address encoding** used by Grover's search circuit.



For the NCBI HV1 experiment, the searchable pattern is an 8-base window, corresponding to 16 DNA-encoding bits. The Grover address register for 16 database records uses 4 qubits.



## Classical Algorithms



### Linear Search



Sequentially examines database records until the target is found.



* Typical search complexity: `O(N)`

* Simple baseline for comparison.



### KMP Search



Uses the Knuth-Morris-Pratt pattern matching approach.



* Pattern preprocessing avoids unnecessary backtracking.

* String-search complexity is `O(N + M)` for a single text/pattern pair.



### Rabin-Karp



Uses rolling hashes to locate candidate matches.



* Average-case string-search complexity is commonly described as `O(N + M)`.

* Worst-case behavior can be `O(NM)` when hash collisions require verification.



Because the implementations count different low-level comparison operations, their raw comparison counts should not be treated as directly interchangeable performance measures.



## Grover's Algorithm



The quantum implementation is located in `quantum/`.



### Oracle



`quantum/oracle.py` constructs a phase oracle that marks the target database index.



### Diffuser



`quantum/grover.py` implements the inversion-about-the-mean diffusion operator:



```text

D = 2|s><s| - I

```



where `|s>` is the uniform superposition.



### Iteration count



The implementation calculates:



```text

k = floor((π/4) × √N)

```



For `N = 16`:



```text

k = 3

```



Grover's success probability oscillates as iterations continue, so using an appropriate iteration count is important.



> The current circuit is naturally demonstrated with power-of-two database sizes. Non-power-of-two database sizes require careful handling of unused computational-basis states and should not be interpreted as fully equivalent without additional circuit design.



## Quantum Simulation



Two Qiskit Aer simulation modes are included.



### Statevector simulation



`quantum/simulator.py` can run the circuit without final measurements and calculate exact state probabilities from the simulated statevector.



### QASM / shot-based simulation



The QASM path executes repeated measurements using a finite number of shots. The current implementation uses **1024 shots** for its QASM experiments.



Because measurements are sampled, QASM frequencies can differ from exact statevector probabilities.



## NCBI GenBank HV1 Dataset



The `ncbi/` package provides an NCBI-based experiment using human mitochondrial DNA.



The current cached dataset contains **16 NCBI GenBank records** with:



* NCBI accession ID

* record name

* sequence description

* extracted 8-base sequence window

* binary DNA encoding

* integer encoding

* HV1 preview

* source

* full sequence length



Example accession IDs include:



```text

JX120769.1

KC533516.1

KC533514.1

KC533510.1

AY195773.1

...

PV560064.1

```



The NCBI search code uses multiple population/geographic-associated search terms and deduplicates retrieved records.



### NCBI email configuration



NCBI requests should identify the user with an email address. The project reads it from the environment variable:



```text

NCBI_EMAIL

```



Do not place a personal email address directly in the source code.



## Repository Structure



```text

dna_quantum_forensics/

│

├── classical/

│   ├── kmp_search.py

│   ├── linear_search.py

│   └── rabin_karp.py

│

├── comparison/

│   ├── benchmark.py

│   ├── charts.py

│   ├── complexity_analysis.py

│   ├── phase7_scaling.py

│   ├── phase7_statistics.py

│   ├── report.py

│   ├── run_phase5.py

│   └── scaling_test.py

│

├── ncbi/

│   ├── final_combined_report.py

│   ├── hv1_database.py

│   ├── hv1_encoder.py

│   ├── search_hv1.py

│   └── verify_phase6.py

│

├── quantum/

│   ├── grover.py

│   ├── iteration_analysis.py

│   ├── oracle.py

│   ├── simulator.py

│   ├── verify_phase4.py

│   └── visualiser.py

│

├── results/

│   ├── chart1_classical_runtime.png

│   ├── chart2_queries_comparison.png

│   ├── chart3_speedup_ratio.png

│   ├── chart4_success_probability.png

│   ├── hv1_ncbi_cache.json

│   ├── iteration_sweep.png

│   ├── phase7_statistics.csv

│   ├── qasm_histogram.png

│   ├── scaled_db_*.json

│   ├── scaling_data.csv

│   └── statevector_probabilities.png

│

├── database.py

├── dna_encoder.py

├── requirements.txt

├── test_ncbi_connection.py

├── utils.py

└── verify_phase1.py

```



## Installation



### 1. Clone the repository



```bash

git clone <YOUR_GITHUB_REPOSITORY_URL>

cd dna_quantum_forensics

```



### 2. Create a virtual environment



Windows PowerShell:



```powershell

python -m venv venv

.\\venv\\Scripts\\Activate.ps1

```



Linux/macOS:



```bash

python -m venv venv

source venv/bin/activate

```



### 3. Install dependencies



```bash

pip install -r requirements.txt

```



## Running the Project



The repository is organized by project phase rather than around a single application entry point.



Examples:



```bash

python verify_phase1.py

python -m quantum.verify_phase4

python -m ncbi.verify_phase6

python -m comparison.scaling_test

```



For NCBI operations, configure `NCBI_EMAIL` before contacting NCBI.



## Results and Reproducibility



The `results/` directory contains generated charts, CSV files, JSON datasets, and cached NCBI data used by the experiments.



Some experiments use randomly selected targets or generated synthetic expansions. Consequently, rerunning certain scripts can produce different target selections or regenerated synthetic records.



The NCBI cache is a snapshot of the dataset used by the current project. Live NCBI retrieval can return different records over time.



The older text reports in the project were generated at earlier stages of development. Their values should not automatically be treated as the current project's source of truth when they differ from the current code or cached dataset.



## Scaling Experiment



The repository includes synthetic scaling experiments for larger database sizes.



The scaling data demonstrates the theoretical/query-count relationship:



```text

Classical search: O(N)

Grover search:    O(√N)

```



For the controlled `N = 16` case:



```text

Classical worst case = 16 record checks

Grover iterations    = 3 oracle queries

Ratio                ≈ 5.33×

```



These scaling experiments are **algorithmic simulations**, not demonstrations that a current quantum computer can perform forensic searches at those database sizes.



## Limitations



1\. The experiments use quantum simulation rather than a production-scale quantum processor.

2\. The reported query-count speedup does not represent end-to-end wall-clock speedup.

3\. Quantum state preparation, oracle construction, database loading, measurement, classical preprocessing, and result interpretation introduce additional costs.

4\. The NCBI experiment uses short 8-base HV1 windows rather than complete forensic STR profiles.

5\. The 16 NCBI records are not independently validated by this project as unrelated individuals.

6\. Synthetic scaling datasets are for algorithmic experimentation and are not equivalent to real forensic databases.

7\. Current Grover circuit handling is most directly aligned with power-of-two database sizes.

8\. Real quantum hardware introduces noise and decoherence that are absent or different in ideal simulation.



## Future Work



Planned extensions include:



* Error mitigation and noise-aware experiments.

* Multi-locus forensic profiles, including STR-based representations.

* Hybrid classical-quantum search pipelines.

* Larger and more systematically curated biological datasets.

* Improved handling of non-power-of-two database sizes.

* Statistical evaluation across repeated target selections.

* Investigation of the practical cost of quantum database/oracle construction.



## Technologies



* **Python**

* **Qiskit**

* **Qiskit Aer**

* **Biopython**

* **NumPy**

* **Pandas**

* **SciPy**

* **Matplotlib**

* **NCBI Entrez / GenBank**



## Disclaimer



This is an academic/research implementation intended to demonstrate quantum search concepts applied to a DNA-pattern-search scenario. It is not a validated forensic identification tool and should not be used for real-world forensic decisions.



## License



Add a license appropriate to your intended use before publishing the repository.



```


