# quantum/visualiser.py
# Generates and saves visualisation plots for Grover's search results.
# Plot 1: Statevector exact probabilities (all 16 states)
# Plot 2: QASM measurement histogram (1024 shots)
# Plot 3: Probability vs iteration count (shows the oscillation effect)

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum.simulator   import full_grover_search
from quantum.grover      import build_grover_circuit, optimal_iterations
from quantum.simulator   import run_statevector
from database            import build_database
from dna_encoder         import get_num_qubits

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def plot_statevector(result: dict, save: bool = True):
    """
    Bar chart of exact probabilities from the statevector simulator.
    Target state bar is highlighted in a distinct colour.
    """
    num_qubits  = result["num_qubits"]
    target_bits = format(result["target_idx"], f'0{num_qubits}b')
    sv_probs    = result["statevector"]["probabilities"]

    # Build full probability array over all 2^n states
    all_states = [format(i, f'0{num_qubits}b') for i in range(2 ** num_qubits)]
    probs      = [sv_probs.get(s, 0.0) for s in all_states]
    colors     = ['#E84040' if s == target_bits else '#5B8DD9' for s in all_states]

    fig, ax = plt.subplots(figsize=(14, 5))
    bars = ax.bar(all_states, probs, color=colors, edgecolor='white', linewidth=0.4)

    # Annotate the target bar
    target_prob = sv_probs.get(target_bits, 0)
    target_bar  = bars[int(target_bits, 2)]
    ax.text(target_bar.get_x() + target_bar.get_width() / 2,
            target_prob + 0.01,
            f"{target_prob:.3f}\n({result['target']['sequence']})",
            ha='center', va='bottom', fontsize=8, color='#E84040', fontweight='bold')

    ax.set_xlabel("Quantum state |bitstring⟩", fontsize=11)
    ax.set_ylabel("Probability", fontsize=11)
    ax.set_title(
        f"Grover's Algorithm — Statevector Probabilities\n"
        f"Target: |{target_bits}⟩ = {result['target']['sequence']} "
        f"(index {result['target_idx']})  |  "
        f"{result['iterations']} iterations  |  N = {result['num_items']}",
        fontsize=11
    )
    ax.set_ylim(0, 1.05)
    ax.tick_params(axis='x', rotation=70, labelsize=7)

    legend = [
        mpatches.Patch(color='#E84040', label=f"Target: {result['target']['sequence']} ({target_prob*100:.1f}%)"),
        mpatches.Patch(color='#5B8DD9', label='Other states'),
    ]
    ax.legend(handles=legend, fontsize=9)
    plt.tight_layout()

    if save:
        path = os.path.join(RESULTS_DIR, "statevector_probabilities.png")
        plt.savefig(path, dpi=150, bbox_inches='tight')
        print(f"Saved: {path}")
    plt.show()


def plot_qasm_histogram(result: dict, save: bool = True):
    """
    Bar chart of QASM shot counts.
    Shows how often each state was measured across 1024 shots.
    """
    num_qubits  = result["num_qubits"]
    target_bits = format(result["target_idx"], f'0{num_qubits}b')
    counts      = result["qasm"]["counts"]
    shots       = result["qasm"]["shots"]

    # Sort by count descending
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    labels = [f"|{b}⟩" for b, _ in sorted_counts]
    values = [c for _, c in sorted_counts]
    colors = ['#E84040' if b == target_bits else '#5B8DD9' for b, _ in sorted_counts]

    fig, ax = plt.subplots(figsize=(14, 5))
    bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=0.4)

    # Annotate top bar
    top_bits, top_count = sorted_counts[0]
    ax.text(0, top_count + 5, f"{top_count} shots\n({top_count/shots*100:.1f}%)",
            ha='center', va='bottom', fontsize=8,
            color='#E84040' if top_bits == target_bits else '#5B8DD9',
            fontweight='bold')

    ax.set_xlabel("Measured state", fontsize=11)
    ax.set_ylabel("Count (out of 1024 shots)", fontsize=11)
    ax.set_title(
        f"Grover's Algorithm — QASM Measurement Histogram\n"
        f"Target: |{target_bits}⟩ = {result['target']['sequence']}  |  "
        f"{shots} shots  |  {result['iterations']} iterations",
        fontsize=11
    )
    ax.tick_params(axis='x', rotation=70, labelsize=8)

    legend = [
        mpatches.Patch(color='#E84040', label=f"Target: {result['target']['sequence']}"),
        mpatches.Patch(color='#5B8DD9', label='Other states'),
    ]
    ax.legend(handles=legend, fontsize=9)
    plt.tight_layout()

    if save:
        path = os.path.join(RESULTS_DIR, "qasm_histogram.png")
        plt.savefig(path, dpi=150, bbox_inches='tight')
        print(f"Saved: {path}")
    plt.show()


def plot_iteration_sweep(save: bool = True):
    """
    Plot how target probability changes as iteration count increases from 0 to 2k.
    Shows the oscillation: probability peaks at k = floor(π/4 · √N), then drops.
    This is a critical insight — running too many iterations HURTS accuracy.
    """
    db         = build_database()
    num_qubits = get_num_qubits(len(db))
    num_items  = len(db)
    target     = __import__('database').get_target()
    target_idx = next(i for i, r in enumerate(db) if r["sequence"] == target["sequence"])
    target_bits = format(target_idx, f'0{num_qubits}b')

    k_optimal = optimal_iterations(num_items)
    max_iters = k_optimal * 3

    iterations_list = list(range(0, max_iters + 1))
    target_probs    = []

    print(f"Running iteration sweep 0 to {max_iters}...")
    for iters in iterations_list:
        if iters == 0:
            # Zero iterations = uniform superposition = probability 1/N
            target_probs.append(1.0 / num_items)
            continue
        qc  = build_grover_circuit(target_idx, num_qubits, num_items, iterations=iters)
        sv  = run_statevector(qc, num_qubits)
        target_probs.append(sv["probabilities"].get(target_bits, 0.0))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(iterations_list, target_probs, 'o-', color='#5B8DD9',
            linewidth=2, markersize=5, label="P(target)")
    ax.axvline(x=k_optimal, color='#E84040', linestyle='--', linewidth=1.5,
               label=f"Optimal k = {k_optimal}")
    ax.axhline(y=1/num_items, color='#888', linestyle=':', linewidth=1,
               label=f"Classical baseline 1/N = {1/num_items:.3f}")

    ax.set_xlabel("Grover iterations", fontsize=11)
    ax.set_ylabel("Target state probability", fontsize=11)
    ax.set_title(
        f"Probability vs Iteration Count  |  N = {num_items}\n"
        f"Optimal iterations k = {k_optimal}  —  probability oscillates",
        fontsize=11
    )
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=9)
    plt.tight_layout()

    if save:
        path = os.path.join(RESULTS_DIR, "iteration_sweep.png")
        plt.savefig(path, dpi=150, bbox_inches='tight')
        print(f"Saved: {path}")
    plt.show()


# ── Run all three plots ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("QUANTUM VISUALISER — generating all plots")
    print("=" * 55)

    result = full_grover_search()

    print("\n[1/3] Statevector probability plot...")
    plot_statevector(result)

    print("\n[2/3] QASM histogram plot...")
    plot_qasm_histogram(result)

    print("\n[3/3] Iteration sweep plot...")
    plot_iteration_sweep()

    print("\nAll plots saved to results/")