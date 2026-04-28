# Lecture 1: Vector Search at Scale & ANN Algorithms

## 1. The Scaling Challenge in Vector Retrieval

While embedding models allow us to represent meaning as vectors, a production-grade RAG system must handle these vectors efficiently. As the knowledge base grows, a naive approach to finding the most relevant documents becomes a computational bottleneck.

## 2. The KNN Bottleneck

The simplest form of vector retrieval is **k-Nearest Neighbors (KNN)**.

- **Mechanism**: The system calculates the distance between the query vector and **every single document** in the database, then sorts them to find the $k$ closest matches.
- **The Problem**: KNN has **linear time complexity $O(N)$**.
  - If you have 1,000 documents, you perform 1,000 calculations.
  - If you have 1 billion documents, you perform 1 billion calculations per query.
- **Impact**: Real-time performance becomes impossible as data scales, leading to high latency and massive resource consumption.

![Complexity Comparison](/rag-lectures/assets/complexity-chart.png)

## 3. Approximate Nearest Neighbors (ANN)

To solve the scaling crisis, we use **Approximate Nearest Neighbors (ANN)** algorithms.

- **The Trade-off**: ANN sacrifices perfect accuracy (guaranteed absolute closest neighbor) for massive gains in speed. It finds vectors that are "close enough" with high probability.
- **The Advantage**: ANN algorithms shift complexity from linear $O(N)$ to **logarithmic $O(\log N)$**, enabling sub-second searches across billions of records.

## 4. Navigable Small World (NSW)

One foundational ANN algorithm is the **Navigable Small World**. It relies on a data structure called a **Proximity Graph**.

![NSW Proximity Graph](/rag-lectures/assets/nsw-graph.png)

### Mechanism:

1. **Graph Construction**: The algorithm builds a web where each document (node) is connected to its nearest neighbors (edges).
2. **Search Traversal**:
   - Start at a **Candidate Vector** (a random entry point).
   - Look at its neighbors and hop to the one closest to the query vector.
   - Repeat until no neighbor is closer than the current candidate.
3. **Outcome**: The algorithm finds a "local optimum." While it might not find the absolute best vector in the entire graph, it finds a very strong match significantly faster than scanning every node.

## 5. Hierarchical Navigable Small World (HNSW)

**HNSW** is the industry standard and a refined evolution of NSW. It optimizes the search further by using a multi-layered hierarchy of proximity graphs.

```mermaid
graph TD
    subgraph Layer_2 ["Layer 2: Sparse (Few Nodes)"]
        L2_A(( )) --- L2_B(( ))
    end
    subgraph Layer_1 ["Layer 1: Moderate Density"]
        L1_A(( )) --- L1_B(( )) --- L1_C(( )) --- L1_D(( ))
    end
    subgraph Layer_0 ["Layer 0: Full Density (All Docs)"]
        L0_A(( )) --- L0_B(( )) --- L0_C(( )) --- L0_D(( )) --- L0_E(( )) --- L0_F(( ))
    end

    Start((Query)) -.-> L2_A
    L2_A -- "Big Jumps" --> L2_B
    L2_B -- "Zoom In" -.-> L1_C
    L1_C -- "Local Search" --> L1_D
    L1_D -- "Final Precision" -.-> L0_F
```

### Why HNSW is Faster:

- **Skip-list Inspiration**: Similar to a skip-list data structure, the top layers have very few nodes.
- **Global to Local**: The algorithm starts at the top layer, making "big jumps" to get into the approximate neighborhood of the query.
- **Layer-by-Layer Refinement**: It drops down through the layers, refining the search in increasingly dense graphs until it reaches the bottom layer (containing all documents) already positioned very close to the optimal result.

## 6. Key Takeaways

1. **Performance**: ANN algorithms are essential for scaling vector search to billions of documents.
2. **Precision vs. Speed**: We accept a slight loss in accuracy to achieve logarithmic search times.
3. **Pre-computation**: Building the proximity graph is computationally intensive, but it is done upfront (indexing) so that queries remain lightning-fast.

---

**Key Takeaway**: K-Nearest Neighbors (KNN) is conceptually simple but fails at scale. Approximate Nearest Neighbors (ANN), and specifically **HNSW**, enables enterprise-grade RAG by using hierarchical proximity graphs to transform a linear search into a fast, logarithmic traversal.
