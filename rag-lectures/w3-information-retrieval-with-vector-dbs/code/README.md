# Information Retrieval with Vector Databases - Module 3

This folder contains the hands-on materials for Module 3, focusing on advanced retrieval techniques using Vector Databases (specifically Weaviate).

## Project Overview

In this assignment, you explore different ways to retrieve information from a corpus of BBC News articles. You will implement and compare:

- **Semantic Search**: Using vector embeddings to find meaning-based matches.
- **BM25 Search**: Traditional keyword-based retrieval.
- **Hybrid Search**: A combination of both semantic and keyword search for improved accuracy.
- **Reranking**: Using a cross-encoder model to re-evaluate the relevance of initially retrieved documents.

## File Descriptions

- **`C1M3_Assignment.ipynb`**: The main notebook for the hands-on exercises.
- **`utils.py`**: Contains core utility functions, including the connection logic for LLMs and the `SentenceTransformer` implementation for embeddings.
- **`weaviate_server.py`**: Logic for initializing and connecting to an **Embedded Weaviate** instance.
- **`flask_app.py`**: A small Flask server used for inference proxy during the assignment.
- **`unittests.py`**: Automated tests to verify your implementation.

## Hands-on Implementation Details

### Local State and Data

During the execution of the notebook, Weaviate creates a local persistent store in the `data/` directory.

- **Database Files (`.db`, `migration*`, `raft/`)**: These are internal state files for the vector database. They are **excluded from Git** (`.gitignore`) because they are session-specific and automatically regenerated when the server starts.
- **`bbc_data.joblib`**: This large binary file contains pre-computed embeddings. It is also excluded from Git to keep the repository lightweight.

### Requirements for Local Execution

To run this module locally, you will need:

1. **API Keys**: Configure your `TOGETHER_API_KEY` in the root `.env` file.
2. **Models Path**: Set `COLLECTIONS_PATH` and `MODEL_PATH` environment variables to ensure Weaviate and the embedding models can store their data locally.
3. **Dependencies**:
   - `weaviate-client` (v4+)
   - `sentence-transformers`
   - `flask`
   - `psutil` (used by `utils.py` to manage ports)

## Architecture Note

This module uses a **Hybrid Search** approach, which combines the strengths of dense vector retrieval (semantic) and sparse vector retrieval (keyword). This is a best practice for production RAG systems to handle both specific keyword queries and broader conceptual questions.
