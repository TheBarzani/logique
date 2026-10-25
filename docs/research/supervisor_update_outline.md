# Outline for supervisor update

## 1. Progress on conditional workspace synthesis

- Investigated reusing input and workspace qubits when a stored Boolean predicate guarantees their value. The computation must preserve that condition, use the borrowed value under the appropriate guard, and restore the qubit afterward.
- In the int2float circuit for one selected output (output 3), combined three guarded target relocations to reduce the allocated qubits from **19 to 16**. This reduces dedicated scratch qubits from seven to four.
- Verified output correctness, phase behavior, and restoration exhaustively, with additional simulations using an entangled reference. The experiments and circuit diagrams are in the [int2float notebook](../../experiments/studies/int2float_conditional_workspace.ipynb).
- The reduction requires additional controls on some gates. Lower qubit count does not yet establish lower depth or lower execution cost after decomposition.
- Next, develop a synthesis algorithm that identifies these opportunities and schedules their use and cleanup. These experiments provide the groundwork. This would be a distinct contribution from the existing graph-coloring paper.

## 2. Refining the existing paper for resubmission

- Begin revising *From Graph k-Coloring to Grover’s Circuits via Logic Synthesis* following the DAC2026 and DATE2026 rejections, using the [saved reviewer feedback](DAC_2026_Reviewer_Feedback.md).
- Broaden comparisons to AIG and k-LUT compilation, including alternative mapping strategies such as LHRS, Bennett, and best-fit.
- Investigate cut-based and ESOP-based balancing for XAG depth reduction, and compare alternative MCT decompositions and their ancilla requirements.
- Add FTQC metrics: T-count, T-depth, and ancilla count. For NISQ, report mapped two-qubit gate count and depth.
- Explain the observed depth and width reductions, including instances where a baseline performs better. Measure synthesis runtime and generated XAG size as graph instances grow.
- Revisit UQS preparation, its rotation-synthesis cost, and consistent preparation across baselines. Address the multi-controlled operation in the diffusion operator when evaluating the complete Grover circuit.
- Strengthen validation across Grover iterations and clarify the paper’s contribution. Prepare a conference or journal resubmission; the venue remains open.
-  To improve the diversity of results one can try LHRS based techniques, AIG based mappings and also different mapping strategies like Bennett, Best-Fit since this coloring benchmark can be benchmarked using logic flows as well.

## 3. Question: when should quantum oracles be lowered?

- Discuss the direction outlined in the [research roadmap](roadmap.md): “When Should Quantum Oracles Be Lowered? Resource Trade-offs in Toffoli and Multi-Controlled Synthesis.”
- Compare early conversion to Toffoli/CNOT gates, retaining larger controlled operations until later, and a mixed approach. Examine the tradeoffs under comparable qubit budgets and compilation settings.
- Ask whether this is a worthwhile research direction, how it relates to conditional workspace synthesis, and how to prioritize it alongside the paper revision.

## 4. Continued study of QEC and FTQC

- Continue studying quantum error correction and fault-tolerant quantum computing through [Quantum error correction and fault tolerance: A comprehensive tutorial](https://arxiv.org/pdf/2605.29137).
- Use this learning to inform the planned fault-tolerant resource evaluation; that cost analysis is still to be done.
