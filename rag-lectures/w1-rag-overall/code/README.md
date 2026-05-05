# Introduction to RAG Systems - Module 1

This folder contains the code and resources for the first assignment of the RAG systems course. In this module, you build a basic Retrieval-Augmented Generation (RAG) pipeline using a dataset of BBC News from 2024.

The goal is to enhance a Large Language Model (Llama 3 8B) with external knowledge, allowing it to accurately answer questions about events that occurred in 2024, which were not part of its original training data.

## File Descriptions

- **`C1M1_Assignment.ipynb`**: The main Jupyter Notebook containing the hands-on exercises. It guides you through implementing a retrieval function, formatting the retrieved data, and generating augmented prompts for the LLM.
- **`utils.py`**: A helper script containing essential functions for the RAG pipeline, including:
  - `retrieve`: Finds the top-k most relevant documents using vector similarity.
  - `generate_with_single_input`: Handles the API calls to the LLM.
  - `read_dataframe` & `pprint`: Data handling and formatted printing.
- **`unittests.py`**: Contains local unit tests to validate your implementation of the assignment exercises.
- **`news_data_dedup.csv`**: A curated dataset containing news headlines, descriptions, and URLs from BBC News (2024). This serves as the external knowledge base for the RAG system.
- **`embeddings.joblib`**: A serialized file containing pre-computed vector embeddings for the news dataset. This allows for fast semantic search without the need to re-compute embeddings during every run.

## Key Concepts Covered

- **Document Retrieval**: Using semantic search to find relevant information in a dataset.
- **Context Augmentation**: Structuring retrieved data into a prompt for the LLM.
- **Comparison Analysis**: Evaluating the difference in response quality between a standard LLM call and a RAG-enhanced call.

## Setup

Ensure you have your environment variables (like API keys) configured as shown in the root directory's `.env` file before running the notebook.
