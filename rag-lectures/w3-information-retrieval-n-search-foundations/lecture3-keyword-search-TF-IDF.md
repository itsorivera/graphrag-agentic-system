# Lecture 3: Keyword Search & TF-IDF Foundations

## 1. Introduction to Lexical Retrieval

Keyword search, also known as **lexical retrieval**, remains a cornerstone of Information Retrieval (IR) and modern Retrieval-Augmented Generation (RAG) pipelines. Despite the rise of semantic search (dense embeddings), keyword search offers distinct advantages in precision for specific entities, technical terms, and exact matches.

## 2. The Representational Model: Bag of Words (BoW)

The fundamental assumption in keyword search is the **Bag of Words** model.

![Bag of Words](/rag-lectures/assets/bag-of-words.png)

_Source: [Retrieval-Augmented Generation by Zain Hasan - DeepLearning.AI](https://www.deeplearning.ai/courses/retrieval-augmented-generation/)_

- **Non-Sequential Representation**: The order of words (syntax/context) is discarded.
- **Frequency-Based Importance**: Relevance is derived from the presence and frequency of specific tokens (keywords).
- **Tokenization**: The process of breaking down text into individual units (tokens) for processing.

## 3. Data Structures and Vector Spaces

To facilitate efficient search across large corpora, text is mapped into a high-dimensional vector space.

### Sparse Vectors

- Each document is represented as a vector in a space where every dimension corresponds to a unique word in the system's global **vocabulary**.
- Because most words in a vocabulary do not appear in any single document, these vectors are **sparse** (predominantly composed of zeros).

### Term-Document Matrix

- A mathematical representation where rows represent terms and columns represent documents.
- Each cell $(i, j)$ indicates the occurrence (or weight) of term $i$ in document $j$.

### The Inverted Index

Modern search engines rely on the **Inverted Index**, which reverses the document-to-term mapping:

![Inverted Index](/rag-lectures/assets/image.png)

_Source: [Retrieval-Augmented Generation by Zain Hasan - DeepLearning.AI](https://www.deeplearning.ai/courses/retrieval-augmented-generation/)_

- **Structure**: A mapping from a **term** to a list of **document IDs** (and frequencies) that contain it.
- **Efficiency**: This allows the system to retrieve only relevant documents during query time rather than scanning every document in the corpus.

## 4. Scoring Foundations: From Counting to Normalization

### Binary and Count-Based Scoring

![Binary and Count-Based Scoring](/rag-lectures/assets/count-term-example.png)

_Source: [Retrieval-Augmented Generation by Zain Hasan - DeepLearning.AI](https://www.deeplearning.ai/courses/retrieval-augmented-generation/)_

- **Binary**: Assigns 1 point if a keyword is present, 0 if not.
- **Count-Based**: Uses raw frequency; documents with more occurrences of a keyword score higher.

### Document Length Normalization

Raw counts create a bias toward longer documents (which naturally contain more words). This is known as **Length Bias**.

- **The Problem**: A 500-page encyclopedia might mention "pizza" 50 times across various chapters, while a 1-page recipe mentions it 10 times. Without normalization, the encyclopedia would rank higher despite the recipe being more relevant to the query.
- **Solution**: Normalize the score by dividing the keyword count by the total number of words in the document.
- **Goal**: Highlight documents where the keyword represents a significant **density** (share of total text), ensuring that short, focused documents are not overshadowed by long, generalist ones.

> [!TIP]
> **Example**:
>
> - **Recipe (100 words)**: "pizza" appears 10 times $\to$ **10% density**.
> - **Encyclopedia (10,000 words)**: "pizza" appears 50 times $\to$ **0.5% density**.
> - **Result**: Normalization ensures the Recipe ranks first because the topic is its primary focus.

## 5. TF-IDF: The Industry Baseline

TF-IDF (**Term Frequency-Inverse Document Frequency**) is an weighting scheme that balances local importance with global rarity.

![TF-IDF](/rag-lectures/assets/tf-idf-example.png)

_Source: [Retrieval-Augmented Generation by Zain Hasan - DeepLearning.AI](https://www.deeplearning.ai/courses/retrieval-augmented-generation/)_

### Term Frequency (TF)

Measures how frequently a term appears in a specific document. High TF suggests high relevance within the context of that document.

### Inverse Document Frequency (IDF)

Measures how "informative" a term is across the entire corpus.

- **Calculation**: $IDF(t) = \log\left(\frac{N}{df(t)}\right)$, where $N$ is the total number of documents and $df(t)$ is the number of documents containing term $t$.
- **Rationale**: Common "filler" words (e.g., "the", "and") have high document frequency and low IDF. Rare, specialized words (e.g., "pizza", "quantum") have low document frequency and high IDF.
- **Log Scaling**: Used to dampen the effect of IDF, preventing extremely rare words from completely dominating the ranking score.

## 6. The TF-IDF Matrix and Retrieval

Multiplying TF by IDF produces a weight that captures a term's significance.

![TF-IDF Matrix](/rag-lectures/assets/tf-idf-matrix2.png)

_Source: [Retrieval-Augmented Generation by Zain Hasan - DeepLearning.AI](https://www.deeplearning.ai/courses/retrieval-augmented-generation/)_

- A high score is achieved by a term having a **high frequency in a given document** and a **low frequency in the overall corpus**.
- **Retrieval Phase**: At query time, the system generates a sparse vector for the prompt and computes the dot product (or sum of weights) against the TF-IDF matrix to rank documents.

## 7. Evolutionary Context: BM25

While TF-IDF is foundational, modern systems typically use **BM25** (Best Matching 25), which introduces non-linear term frequency saturation and improved document length normalization.

---

**Key Takeaway**: Keyword search via TF-IDF provides a robust, interpretable, and computationally efficient baseline for retrieval, ensuring that rare and specific terms drive the ranking process.
