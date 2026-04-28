# Lecture 5: Introduction to Semantic Search

## 1. Beyond Keywords: The Semantic Advantage

Semantic search addresses the fundamental limitations of lexical retrieval by matching documents based on **intent and meaning** rather than exact character sequences.

- **Handling Synonyms**: Keyword search (lexical) fails to connect terms like "happy" and "glad" because they share no tokens. Semantic search recognizes their conceptual overlap.
- **Solving Polysemy (Ambiguity)**: Semantic search can distinguish between "Python" (the programming language) and "Python" (the snake) by analyzing the surrounding context of the query.

## 2. Theoretical Foundation: Vector Space Representation

The core of semantic search is the transformation of text into a mathematical representation within a high-dimensional vector space.

![Semantic Clustering](/rag-lectures/assets/semantic-clustering.png)

- **Embedding Models**: These are specialized mathematical models (often neural networks) that map words, sentences, or entire documents to specific coordinates (**vectors**) in space.
- **The Proximity Principle**: In a well-trained embedding model, semantically similar concepts are placed close together. Concepts like "cuisine" and "food" will cluster in one region, while unrelated concepts like "trombone" and "cat" will be embedded far apart.
- **High Dimensionality**: While 2D/3D visualizations are helpful for intuition, production embedding models typically use **hundreds or thousands of components** (dimensions), providing the flexibility needed to capture nuanced linguistic relationships.

![Vector Space Dimensions](/rag-lectures/assets/vector-space-dims.png)
_Source: [Retrieval-Augmented Generation by Zain Hasan - DeepLearning.AI](https://www.deeplearning.ai/courses/retrieval-augmented-generation/)_

## 3. Granularity of Embeddings

Embedding models exist for various levels of text hierarchy, each outputting a single vector that specifies a unique point in space:

![Granularity of Embeddings](/rag-lectures/assets/granularity-of-embeddings.png)
_Source: [Retrieval-Augmented Generation by Zain Hasan - DeepLearning.AI](https://www.deeplearning.ai/courses/retrieval-augmented-generation/)_

- **Word Embeddings**: Capture the semantics of individual terms.
- **Sentence Embeddings**: Capture the intent and context of a complete thought.
- **Document Embeddings**: Summarize the collective meaning of larger text blocks or entire articles.

## 4. Measuring Similarity: Distance Metrics

To quantify relevance, the system measures the distance between the query vector and the document vectors.

![Distance Metrics](/rag-lectures/assets/distance-metrics.png)

### Euclidean Distance (L2)

- **Definition**: The "straight-line" distance between two points in space, calculated using a multi-dimensional version of the Pythagorean theorem.
- **Insight**: Useful for absolute displacement, though in very high dimensions, points tend to become equidistant (the "curse of dimensionality").

### Cosine Similarity

- **Definition**: Measures the cosine of the angle between two vectors.
- **Range**: **1** (identical direction/highest similarity) to **-1** (exact opposite).
- **Advantage**: It focuses purely on the **orientation/direction** of the vectors rather than their magnitude, making it the industry standard for text retrieval.

### Dot Product

- **Definition**: The sum of the products of corresponding components.
- **Relationship**: If vectors are normalized (magnitude of 1), the dot product is mathematically equivalent to Cosine Similarity.

## 5. The Semantic Search Workflow

The retrieval process follows a systematic cycle that mirrors keyword search but uses different underlying logic:

![Semantic Search Workflow](/rag-lectures/assets/semantic-search-workflow.png)
_Source: [Retrieval-Augmented Generation by Zain Hasan - DeepLearning.AI](https://www.deeplearning.ai/courses/retrieval-augmented-generation/)_

1. **Projection (Indexing)**: Every document in the corpus is passed through the embedding model to generate a static vector.
2. **Query Embedding**: At search time, the user's prompt is embedded using the **same model** to generate a query vector.
3. **Similarity Search**: The system calculates the distance (typically Cosine Similarity) between the query vector and all document vectors.
4. **Ranking**: Documents are sorted by proximity (shortest distance/highest similarity) and returned to the user.

---

**Key Takeaway**: Semantic search shifts the retrieval paradigm from "matching tokens" to "matching concepts." By mapping language into a structured vector space, we can quantify conceptual relevance with mathematical precision, enabling more intuitive and context-aware RAG systems.
