# LLM Decoding Parameters: A Technical Reference for AI Engineers

This document provides a rigorous explanation of the primary hyperparameters used to control the token generation process in Large Language Models (LLMs).

## 1. The Mathematical Foundation: Softmax and Logits

At the final stage of inference, an LLM produces a vector of **logits** ($z$), which are the raw, unnormalized scores for every token in the model's vocabulary. To transform these into a probability distribution, the **Softmax** function is applied:

$$P(x_i) = \frac{\exp(z_i)}{\sum_j \exp(z_j)}$$

Decoding parameters intercept this process to modify the shape of the distribution or filter the candidate set before a token is sampled.

---

## 2. Temperature ($T$)

Temperature is a scaling factor applied to the logits before the Softmax function. It controls the "sharpness" of the probability distribution.

$$P(x_i) = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}$$

### Engineering Impact:

- **Low Temperature ($T \to 0$):** The distribution becomes highly peaked. The difference between the top token and the others is amplified. At $T=0$, this results in **Greedy Search**, where the model always picks the most probable token.
  - _Usage:_ Deterministic tasks like code generation, mathematical reasoning, and structured data extraction.
- **Neutral Temperature ($T = 1.0$):** The model samples directly from the probability distribution it learned during training.
- **High Temperature ($T > 1.0$):** The distribution is flattened (entropy increases). Low-probability tokens become more likely to be selected.
  - _Usage:_ Creative brainstorming, poetry, or avoiding repetitive "stilted" responses.
  - _Risk:_ Values $>1.5$ often lead to incoherent "hallucinations" as structural linguistic constraints are ignored.

---

## 3. Top-K Sampling

Top-K is a hard filtering strategy that restricts the model's choice to the $K$ tokens with the highest probability.

### Engineering Impact:

- **Mechanism:** All tokens outside the top $K$ positions have their probabilities set to $0$ before sampling.
- **Range ($1$ to $100$):**
  - **Small $K$ (e.g., $K=10$):** Ensures high focus and eliminates "tail" noise, but may result in repetitive or overly generic text.
  - **Large $K$ (e.g., $K=50+$):** Allows for more diverse vocabulary by including lower-probability (but potentially more interesting) tokens.
- **Limitation:** Top-K is **static**. It does not account for the shape of the distribution. If the top 100 tokens are all equally valid, $K=50$ arbitrarily cuts off 50 good options.

---

## 4. Top-P (Nucleus Sampling)

Top-P sampling (Nucleus Sampling) defines a threshold $P$ and selects the smallest set of tokens whose **cumulative probability** exceeds $P$.

### Engineering Impact:

- **Mechanism:** The size of the candidate set ($V^{(p)}$) is dynamic:
  $$\sum_{x \in V^{(p)}} P(x) \ge P$$
- **Range ($0.1$ to $1.0$):**
  - **Low $P$ (e.g., $0.1$):** Filters out most of the distribution, keeping only the "core" of high-confidence tokens.
  - **High $P$ (e.g., $0.9$ or $0.95$):** Allows for a "long tail" while still clipping the extreme outliers.
- **Advantage:** It is **dynamic**. If the model is confident, the nucleus is small. If the model is uncertain, the nucleus expands, capturing a wider range of viable linguistic paths.

---

## 5. Engineering Best Practices & Use Cases

| Parameter         | Recommended Range         | Use Case                                       |
| :---------------- | :------------------------ | :--------------------------------------------- |
| **Deterministic** | $T: 0.0$                  | Code, Math, JSON Extraction, RAG Grounding.    |
| **Balanced**      | $T: 0.7$, $P: 0.9$        | Chatbots, general assistance, summarization.   |
| **Creative**      | $T: 1.0 - 1.2$, $P: 0.95$ | Storytelling, brainstorming, creative writing. |

### Technical Tips:

1.  **Mutual Exclusivity:** While you can use both Top-K and Top-P, it is standard practice to fix one (usually $K=50$ or $K=0$) and tune $P$.
2.  **RAG Optimization:** In Retrieval-Augmented Generation, minimizing hallucinations is paramount. Use $T < 0.3$ to ensure the model prioritizes the provided context over its own internal stochastic weights.
3.  **Seed Values:** For reproducibility in testing, use a fixed `seed` parameter alongside your decoding settings.
