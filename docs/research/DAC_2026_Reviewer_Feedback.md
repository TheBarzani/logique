# DAC 2026 Reviews for Submission #511

**Title:** From Graph k-Coloring to Grover's Circuits via Logic Synthesis

**Authors:** Ismael Barzani and Sébastien Le Beux

## Reviewer 1

### Reviewer’s Scores

| Criterion | Score (1–5) |
| --- | --- |
| Clarity / Writing Style | 4 |
| Originality / Innovativeness | 2 |
| Impact of Ideas and/or Results | 2 |
| OVERALL RECOMMENDATION | 2 |

### Summarize shortly the contributions of the paper in your own words.

This work presents an oracle synthesis framework designed to generate MCT-free oracles for Grover's search algorithm, which is applied to the graph k-coloring problem. While Grover's algorithm offers a theoretical quadratic speedup, existing synthesis approaches for the oracle circuit heavily rely on Multi-Controlled Toffoli (MCT) gates. Since MCT gates are not native to quantum hardware, decomposing them into elementary gates incurs significant overheads in circuit depth, width, and gate count. To address this, the authors propose a synthesis framework that avoids generating MCT gates directly during the synthesis phase. By integrating multiple existing techniques, including UQS state preparation and diffusion operator preparation, the proposed approach yields superior overall improvements in circuit width, depth, and gate count compared to the state-of-the-art.

### Strengths

- The approach of avoiding MCT gates at the synthesis level (via GF(2) Boolean functions and XAGs), rather than relying on post-synthesis decomposition, is a key contribution of this work.
- Compared to the state-of-the-art, the proposed method achieves comprehensive improvements in circuit depth, width, and gate count. This demonstrates that the framework can generate MCT-free circuits without increasing the qubit count.
- The paper is well-written and easy to follow.

### Weaknesses

- The authors must clarify the specific novelty beyond a simple combination of existing techniques. Additionally, a deeper explanation of how the proposed approach achieves lower circuit width overhead than MCT-based baselines is also necessary.

### Main Discussion of Paper

Although the proposed method avoids generating MCTs, it still requires additional ancilla qubits, which typically increases circuit width (qubit count). However, the results show a lower circuit width compared to other methods that do generate MCTs. The authors should provide a deeper discussion on why the proposed approach achieves lower width overhead.

The paper primarily integrates various existing methods. While the overall results are improved, the specific novelty and contribution of this work need to be explicitly clarified to distinguish it from a simple combination of known techniques.

In Section 4.3 (Comparison of synthesis circuits), the experiments lack an accuracy comparison for larger graph instances. This omission raises concerns regarding the practical usability of the generated circuits.

The "NISQ" appearing in the top-right corner of Page 1 should include its full term, which is introduced on Page 2. It should be spelled out upon first mention.

There is an inconsistency in variable notation (x v.s. v) between Figure 5 and Equation 4.

In the current accuracy (success probability) experiments, only a single Grover iteration is performed. However, the reported accuracy for large graph instances is notably low. The reviewer suggests conducting an additional experiment with an increased number of Grover iterations on these large instances to evaluate and compare the resultant accuracy. Furthermore, the authors should compare the circuit width overhead of the proposed approach with the overhead resulting from the decomposition of MCT gates.

## Reviewer 2

### Reviewer’s Scores

| Criterion | Score (1–5) |
| --- | --- |
| Clarity / Writing Style | 4 |
| Originality / Innovativeness | 3 |
| Impact of Ideas and/or Results | 3 |
| OVERALL RECOMMENDATION | 3 |

### Summarize shortly the contributions of the paper in your own words.

1. The paper presents an automated end-to-end HLS flow that compiles graph k-coloring into Grover circuits using GF(2) Boolean compilation, XAG-based logic synthesis, and uniform state preparation, aiming to eliminate multi-controlled Toffoli (MCT) gates and their decomposition overhead.
2. The experimental evaluation reports substantial resource savings versus MCT-based baselines, including 49.4% lower circuit depth, 60.1% fewer gates, and 41.7% reduced width.
3. Hardware runs on IBM's Heron-r1 are used to support the practical impact, suggesting that the resulting shallower circuits achieve improved noise resilience and higher success probabilities.

### Strengths

1. The paper is well-written and easy to follow.
2. MCT decomposition overhead is a real pain point and the paper makes the case well.
3. Demonstrating noise-efficiency is a plus.

### Weaknesses

1. Nowadays, due to advancement of FTQC, readers expect T-count or T-depth as metrics, and for NISQ they also expect mapped two-qubit gate counts. These are missing.

### Main Discussion of Paper

The paper proposes an end-to-end high-level synthesis (HLS) flow that takes a graph k-coloring instance and emits a Grover circuit whose oracle avoids multi-controlled Toffoli (MCT) gates. The paper is well-written and novel with respect to state-of-the-art works. The methods used in this paper are not fundamentally new; the work is largely incremental, but it delivers a more efficient circuit-synthesis pipeline. My suggestions are as follows:

1. You should include more standard evaluation metrics: given recent advances in FTQC, readers typically expect T-count or T-depth, and for NISQ settings they also expect two-qubit gate counts after mapping.

2. What is the runtime and size of the generated XAGs as the size of the graphs grow? Does logic synthesis ever become a bottleneck? Please comment.

## Reviewer 3

### Reviewer’s Scores

| Criterion | Score (1–5) |
| --- | --- |
| Clarity / Writing Style | 4 |
| Originality / Innovativeness | 2 |
| Impact of Ideas and/or Results | 2 |
| OVERALL RECOMMENDATION | 1 |

### Summarize shortly the contributions of the paper in your own words.

The work uses internal logic synthesis and boolean function based representations to map the k colouring problem into a boolean circuit and eventually to a quantum circuit using quantum logic synthesis based mapping techniques. Doing this author finds represenation for the grover oracle in an XAG circuit and maps it to a quantum circuit without using any MCT gates. In this mapping the paper finds improvment in success probabilities and other metrics like depth, width and gate counts from previous works.

### Strengths

1. Brings a new approach to the K-coloring problem in quantum using logic synthesis optimisations

### Weaknesses

1. The goal of optimisation for better decomposition of MCT approach would be better than generating plain XAG mappings (like conditionally clean ancilla)

2. Can utilise more techniques for mapping strategies using more internal logic representations (k-LUT,AIG)

3. Could have used operations for depth reduction on the XAG like cut/esop based balancing


### Main Discussion of Paper

Circuit optimisations for the graph coloring problem using XAG gates is an interesting problem. The MCT free decomposition is not an absolute goal towards optimising a boolean function, a lot more improvements can be achieved using balancing techniques and optimisations on the XAG itself. The methods used work on generating an XAG and mapping it to a quantum circuit which could be improved further by using better decomposition methods and optimisations on the logic graph itself. To improve the diversity of results one can try lhrs based techniques, AIG based mappings and also different mapping strategies like bennett, best-fit since this coloring benchmark can be benchmarked using logic flows as well.

## Reviewer 4

### Reviewer’s Scores

| Criterion | Score (1–5) |
| --- | --- |
| Clarity / Writing Style | 3 |
| Originality / Innovativeness | 4 |
| Impact of Ideas and/or Results | 3 |
| OVERALL RECOMMENDATION | 2 |

### Summarize shortly the contributions of the paper in your own words.

The paper proposes an automated high-level synthesis flow that compiles graph k-coloring instances into Grover circuits with MCT-free oracles by translating edge constraints into GF(2) Boolean functions, synthesizing them as XAG networks, and integrating efficient uniform quantum superposition state preparation. The approach significantly reduces circuit depth, width, and gate count compared to existing MCT-based methods.

### Strengths

1. Provides a complete workflow from a high-level graph description to an executable, optimized quantum circuit for the graph coloring oracle, avoiding multi-controlled Toffoli gates at the synthesis level.
2. Employs the Shukla-Vedula algorithm for UQS to ensure that only valid colorings are prepared in the initial superposition, thereby improving the success probability and yielding clear quantitative improvements in circuit depth, width, and gate count over strong baselines.

### Weaknesses

1. The UQS preparation relies on rotation gates whose fault-tolerant implementations typically incur significant overhead due to decomposition into Clifford+T primitives.
2. The depth-optimized Belletti-Simple[3] baseline still outperforms the proposed method in certain specific instances.

### Main Discussion of Paper

This paper tackles a well-known bottleneck in Grover-based quantum algorithms for graph k-coloring: the heavy reliance on multi-controlled Toffoli (MCT) gates in oracle construction. The authors correctly identify that decomposing MCT gates after synthesis introduces large overheads in depth, width, and ancilla usage.

The compilation of edge constraints into GF(2) Boolean functions explicitly avoid multi-fan-in AND gates. This design choice aligns naturally with XAG logic networks. The integration of uniform quantum superposition (UQS) preparation is another important aspect. By restricting the search space to valid color encodings, the authors reduce unnecessary overhead and improve success probability. The experimental evaluation is thorough and the reported average reductions (49% depth, 42% width, 60% gate count) are convincing.

However, the diffusion operator still conceptually involves multi-controlled behavior, and scalability remains an open question: while the synthesis flow scales algorithmically. Also, while the paper measures depth, width, and gate count in a Clifford+Toffoli cost model, a more explicit discussion of Clifford+T cost (especially T-count implications of UQS rotations and AND constructions) would strengthen the relevance to fault-tolerant settings.

Overall, the paper presents a technically competent synthesis pipeline and demonstrates meaningful constant-factor improvements over selected baselines. However, its claims regarding the avoidance of multi-controlled gates and scalability would benefit from a deeper cost-model analysis. Furthermore, while UQS preparation is presented as a key advantage, it relies heavily on rotation gates that are expensive to realize in fault-tolerant settings. The absence of any analysis of rotation counts, decomposition costs, or the resulting T-count and T-depth significantly limits the applicability of the reported results to realistic fault-tolerant architectures.
